#!/usr/bin/env python3
"""Patch Tasks.org desktop build so CalDAV/Etebase/Microsoft/Google Tasks sync
run without a GitHub Sponsor / Play subscription. For personal fork builds only.

Idempotent: safe to run repeatedly (no-op if already applied)."""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'


def patch_sync_runner():
    path = os.path.join(ROOT, 'composeApp/src/commonMain/kotlin/org/tasks/sync/SyncRunner.kt')
    src = open(path, encoding='utf-8').read()
    src = src.replace(
        'val hasPro = hasTasksOrg || subscriptionProvider.subscription.first() != null',
        'val hasPro = true',
    )
    src = src.replace(
        'googleAndMicrosoftPro = hasPro || !subscriptionProvider.googleAndMicrosoftRequirePro,',
        'googleAndMicrosoftPro = true,',
    )
    open(path, 'w', encoding='utf-8').write(src)
    print(f"Patched {path}")


def patch_add_account_screen():
    path = os.path.join(ROOT, 'kmp/src/commonMain/kotlin/org/tasks/compose/accounts/AddAccountScreen.kt')
    src = open(path, encoding='utf-8').read()

    src = src.replace(
        '\n                val isDesktop = configuration.billingProvider == BillingProvider.PADDLE\n',
        '\n',
    )

    free_block = (
        '\n'
        '                    if (configuration.supportsMicrosoft) add(Platform.MICROSOFT)\n'
        '                    if (configuration.supportsGoogleTasks) add(Platform.GOOGLE_TASKS)\n'
        '                    if (configuration.supportsCaldav) add(Platform.CALDAV)\n'
        '                    if (configuration.supportsEteSync) add(Platform.ETEBASE)'
    )
    src = re.sub(
        r'val freeAccounts = buildList \{.*?\}',
        'val freeAccounts = buildList {' + free_block + '\n                }',
        src,
        flags=re.DOTALL,
    )

    pro_block = (
        '\n'
        '                    if (configuration.supportsOpenTasks) add(Platform.DAVX5)'
    )
    src = re.sub(
        r'val proAccounts = buildList(?:<Platform>)? \{.*?\}',
        'val proAccounts = buildList<Platform> {' + pro_block + '\n                }',
        src,
        flags=re.DOTALL,
    )

    open(path, 'w', encoding='utf-8').write(src)
    print(f"Patched {path}")


def patch_app_kt():
    """Remove the pricing redirect that blocks CalDAV/Etebase/Google/MS sign-in
    when the user does not have a Pro subscription (App.kt onboarding flow)."""
    path = os.path.join(ROOT, 'composeApp/src/commonMain/kotlin/org/tasks/App.kt')
    src = open(path, encoding='utf-8').read()

    block = (
        '                                val sellsSubscriptions = configuration.billingProvider == org.tasks.billing.BillingProvider.PADDLE\n'
        '                                    || configuration.appStore == AppStore.APP_STORE\n'
        '                                if (sellsSubscriptions && !addAccountViewModel.hasPro) {\n'
        '                                    when (platform) {\n'
        '                                        Platform.CALDAV, Platform.ETEBASE, Platform.GOOGLE_TASKS, Platform.MICROSOFT -> {\n'
        '                                            backStack.push(PricingDestination(mode = PricingMode.NYP_ONLY, source = platform.name))\n'
        '                                            return@AddAccountScreen\n'
        '                                        }\n'
        '                                        else -> {}\n'
        '                                    }\n'
        '                                }'
    )
    if block in src:
        src = src.replace(block, '')
        open(path, 'w', encoding='utf-8').write(src)
        print(f"Patched {path}")
    else:
        print(f"Already patched or block not found in {path}")


if __name__ == '__main__':
    patch_sync_runner()
    patch_add_account_screen()
    patch_app_kt()
    print("Done.")
