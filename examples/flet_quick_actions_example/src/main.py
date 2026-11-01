import logging
import sys
import traceback

# ---------------------------------------------------------------------------
# Flet logging cookbook pattern
# https://flet.dev/docs/cookbook/logging
#
# Configure logging BEFORE calling ft.run(). While troubleshooting the black
# screen we use DEBUG; switch to INFO for normal use.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
# Raise Flet's own logger to DEBUG so framework/transport details are visible.
logging.getLogger("flet").setLevel(logging.DEBUG)
# Enable the two verbose loggers only when you need deep control-tree diagnostics.
# logging.getLogger("flet_object_patch").setLevel(logging.DEBUG)
# logging.getLogger("flet_components").setLevel(logging.DEBUG)

logger = logging.getLogger("quick_actions_example")

# ---------------------------------------------------------------------------
# STAGE 0 — prove Python started at all.
# ---------------------------------------------------------------------------
logger.debug("=" * 70)
logger.debug("[BOOT-0] main.py is executing")
logger.debug("[BOOT-0] Python %s", sys.version)
logger.debug("[BOOT-0] Platform: %s", sys.platform)
logger.debug("[BOOT-0] sys.path[0]: %s", sys.path[0] if sys.path else "?")
logger.debug("=" * 70)


# ---------------------------------------------------------------------------
# STAGE 1 — import flet.
# ---------------------------------------------------------------------------
try:
    import flet as ft

    logger.debug("[BOOT-1] flet imported OK")
except Exception:
    logger.exception("[BOOT-1] FATAL: import flet failed")
    raise


# ---------------------------------------------------------------------------
# STAGE 2 — import the extension. This is the most likely place a black
# screen originates: if the extension's Python package is broken or its
# Flutter side isn't registered, this import may fail or hang.
# ---------------------------------------------------------------------------
try:
    from flet_quick_actions import QuickActions, ShortcutItem

    logger.debug("[BOOT-2] flet_quick_actions imported OK")
except Exception:
    logger.exception("[BOOT-2] FATAL: import flet_quick_actions failed")
    raise


# ---------------------------------------------------------------------------
# STAGE 3 — build the UI.
# ---------------------------------------------------------------------------
def main(page: ft.Page):
    logger.debug("[MAIN] main() entered")

    try:
        page.title = "Quick Actions Demo"
        logger.debug("[MAIN] page.title set")

        status = ft.Text("no action set", size=20, weight=ft.FontWeight.BOLD)
        hint = ft.Text(
            "On the home screen, long-press the app icon to get "
            "'Action one' or 'Action two'. Tapping one should change the title.",
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        logger.debug("[MAIN] text controls created")

        # --- construct the service ---
        try:
            qa = QuickActions()
            logger.debug("[MAIN] QuickActions created: %r", qa)
        except Exception:
            logger.exception("[MAIN] FATAL: QuickActions() raised")
            page.add(ft.Text(f"QuickActions() failed:\n{traceback.format_exc()}"))
            return

        # --- event handler ---
        def on_action(e: ft.ControlEvent):
            logger.debug("[EVENT] on_action fired: data=%r", e.data)
            status.value = e.data
            page.update()

        qa.on_action = on_action
        logger.debug("[MAIN] on_action attached")

        # --- clear handler ---
        async def clear_shortcuts(_):
            logger.debug("[EVENT] clear_shortcuts clicked")
            try:
                await qa.clear_shortcuts()
                status.value = "Shortcuts cleared."
                logger.debug("[EVENT] clear_shortcuts OK")
            except Exception:
                logger.exception("[EVENT] clear_shortcuts FAILED")
                status.value = f"clear failed: {sys.exc_info()[1]}"
            page.update()

        # --- install handler ---
        async def install_shortcuts(_):
            logger.debug("[EVENT] install_shortcuts clicked")
            try:
                await qa.set_shortcuts(
                    [
                        ShortcutItem(
                            type="new_message",
                            localized_title="New Message",
                            icon="ic_new_message",
                        ),
                        ShortcutItem(
                            type="search",
                            localized_title="Search",
                            icon="ic_search",
                        ),
                    ]
                )
                status.value = "New Shortcuts installed - long-press the app icon."
                logger.debug("[EVENT] install_shortcuts OK")
            except Exception:
                logger.exception("[EVENT] install_shortcuts FAILED")
                status.value = f"install failed: {sys.exc_info()[1]}"
            page.update()

        # --- cold-start setup task ---
        async def setup():
            logger.debug("[SETUP] setup() started")
            try:
                await qa.set_shortcuts(
                    [
                        ShortcutItem(
                            type="action_one",
                            localized_title="Action one",
                            localized_subtitle="Action one subtitle",
                            icon="AppIcon",
                        ),
                        ShortcutItem(
                            type="action_two",
                            localized_title="Action two",
                            icon="ic_launcher",
                        ),
                    ]
                )
                logger.debug("[SETUP] set_shortcuts OK")

                if status.value == "no action set":
                    status.value = "actions ready"
                page.update()
                logger.debug("[SETUP] UI updated")

                pending = await qa.get_pending_action()
                logger.debug("[SETUP] get_pending_action -> %r", pending)
                if pending:
                    on_action(ft.ControlEvent(control=qa, name="action", data=pending))
            except Exception:
                logger.exception("[SETUP] setup() FAILED")
                try:
                    status.value = f"setup failed: {sys.exc_info()[1]}"
                    page.update()
                except Exception:
                    logger.exception("[SETUP] failed to display error on page")
            finally:
                logger.debug("[SETUP] setup() finished")

        # --- assemble the page ---
        page.add(
            ft.SafeArea(
                content=ft.Column(
                    [
                        status,
                        hint,
                        ft.Button("Install shortcuts", on_click=install_shortcuts),
                        ft.Button("Clear shortcuts", on_click=clear_shortcuts),
                    ],
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        )
        logger.debug("[MAIN] page.add() done — UI should now be visible")

        page.run_task(setup)
        logger.debug("[MAIN] setup task scheduled")

    except Exception:
        logger.exception("[MAIN] FATAL: main() raised")
        try:
            page.add(ft.Text(f"main() failed:\n{traceback.format_exc()}"))
        except Exception:
            logger.exception("[MAIN] failed to display error on page")


# ---------------------------------------------------------------------------
# STAGE 4 — hand off to Flet.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.debug("[BOOT-4] calling ft.run(main)")
    try:
        ft.run(main)
        logger.debug("[BOOT-4] ft.run() returned normally")
    except Exception:
        logger.exception("[BOOT-4] FATAL: ft.run() raised")
        raise
