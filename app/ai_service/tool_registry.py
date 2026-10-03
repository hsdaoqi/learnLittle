"""工具注册表：组名 → 工具名，名称全局唯一。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict
    fn: Callable[..., Any] | None
    group: str = "base"
    parallel_safe: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self._groups: dict[str, list[str]] = {}
        self._specs: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._specs:
            raise ValueError(f"工具名冲突: {spec.name}")
        self._specs[spec.name] = spec
        self._groups.setdefault(spec.group, []).append(spec.name)

    def register_group(self, group: str, names: list[str]) -> None:
        self._groups[group] = list(names)

    def get(self, name: str) -> ToolSpec | None:
        return self._specs.get(name)

    def resolve(self, groups: list[str] | None = None) -> list[ToolSpec]:
        if groups is None:
            names = [name for names in self._groups.values() for name in names]
        else:
            names = []
            seen: set[str] = set()
            for group in groups:
                for name in self._groups.get(group, []):
                    if name not in seen:
                        seen.add(name)
                        names.append(name)
        return [self._specs[name] for name in names if name in self._specs]

    def unregister(self, name: str) -> None:
        self._specs.pop(name, None)
        for names in self._groups.values():
            while name in names:
                names.remove(name)

    def bind(self, builtins: dict[str, Callable]) -> dict[str, Callable]:
        return {
            spec.name: spec.fn or builtins[spec.name]
            for spec in self.resolve()
            if spec.fn is not None or spec.name in builtins
        }

    def groups_for(self, name: str) -> list[str] | None:
        spec = self.get(name)
        if spec is None:
            return None
        groups = ["base", spec.group]
        if spec.group == "note_write":
            groups.append("note_read")
        return list(dict.fromkeys(groups))

registry = ToolRegistry()
