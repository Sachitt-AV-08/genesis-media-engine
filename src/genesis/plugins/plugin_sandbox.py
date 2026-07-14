from __future__ import annotations


class PluginSandbox:
    def review_command(self, command: list[str] | str) -> dict:
        text = " ".join(command) if isinstance(command, list) else command
        unsafe = any(token in text.lower() for token in ("&&", "|", "powershell", "cmd.exe", "rm -rf", "del /s"))
        return {"approved": not unsafe, "reason": "unsafe shell metacharacters blocked" if unsafe else "command shape accepted"}
