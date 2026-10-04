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
    # Match both `buildList {` and `buildList<Platform> {` so it is idempotent.
    src = re.sub(
        r'val proAccounts = buildList(?:<Platform>)? \{.*?\}',
        'val proAccounts = buildList<Platform> {' + pro_block + '\n                }',
        src,
        flags=re.DOTALL,
    )

    open(path, 'w', encoding='utf-8').write(src)
    print(f"Patched {path}")


if __name__ == '__main__':
    patch_sync_runner()
    patch_add_account_screen()
    print("Done.")
