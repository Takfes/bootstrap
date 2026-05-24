#!/usr/bin/env python3
"""
Skill Transfer: Scan, compare, and consolidate skills across repositories.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class SkillInfo:
    """Metadata about a skill."""
    name: str
    repo: str  # .claude, .gemini, .agents
    path: Path
    version: Optional[str] = None
    description: Optional[str] = None
    file_hash: Optional[str] = None
    file_count: int = 0
    total_size: int = 0


def hash_directory(path: Path) -> str:
    """Compute SHA256 hash of all files in a directory."""
    hasher = hashlib.sha256()
    for file_path in sorted(path.rglob("*")):
        if file_path.is_file():
            with open(file_path, "rb") as f:
                hasher.update(f.read())
    return hasher.hexdigest()


def extract_metadata(skill_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extract version and description from SKILL.md frontmatter."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None, None

    try:
        with open(skill_md, "r") as f:
            content = f.read()
            # Extract YAML frontmatter
            if content.startswith("---"):
                end_marker = content.find("---", 3)
                if end_marker != -1:
                    yaml_str = content[3:end_marker].strip()
                    version = None
                    description = None

                    # Simple regex-based YAML parsing
                    version_match = re.search(r'version:\s*([^\n]+)', yaml_str)
                    if version_match:
                        version = version_match.group(1).strip().strip("'\"")

                    desc_match = re.search(r'description:\s*([^\n]+)', yaml_str)
                    if desc_match:
                        description = desc_match.group(1).strip().strip("'\"")

                    return version, description
    except Exception:
        pass

    return None, None


def scan_repository(repo_path: Path, repo_name: str) -> Dict[str, SkillInfo]:
    """Scan a repository for skills."""
    skills = {}
    skills_dir = repo_path / ".claude" / "skills" if repo_name == ".claude" else \
                 repo_path / ".gemini" / "skills" if repo_name == ".gemini" else \
                 repo_path / ".agents" / "skills"

    if not skills_dir.exists():
        return skills

    for skill_folder in skills_dir.iterdir():
        if not skill_folder.is_dir():
            continue

        skill_name = skill_folder.name
        version, description = extract_metadata(skill_folder)
        file_hash = hash_directory(skill_folder)
        file_count = sum(1 for _ in skill_folder.rglob("*") if _.is_file())
        total_size = sum(_.stat().st_size for _ in skill_folder.rglob("*") if _.is_file())

        skills[skill_name] = SkillInfo(
            name=skill_name,
            repo=repo_name,
            path=skill_folder,
            version=version,
            description=description,
            file_hash=file_hash,
            file_count=file_count,
            total_size=total_size,
        )

    return skills


def find_conflicts(all_skills: Dict[str, List[SkillInfo]]) -> Tuple[List[str], Dict[str, List[SkillInfo]], Dict[str, List[SkillInfo]]]:
    """Classify skills into auto-resolvable and conflicts."""
    auto_resolvable = {}
    conflicts = {}

    for skill_name, skill_list in all_skills.items():
        if len(skill_list) == 1:
            # Only in one repo
            auto_resolvable[skill_name] = skill_list
        else:
            # In multiple repos
            hashes = set(s.file_hash for s in skill_list)
            if len(hashes) == 1:
                # All identical
                auto_resolvable[skill_name] = skill_list
            else:
                # Hashes differ - conflict
                conflicts[skill_name] = skill_list

    return list(auto_resolvable.keys()), auto_resolvable, conflicts


def generate_report(
    project_path: Path,
    source_repo: str,
    dest_repos: List[str],
) -> str:
    """Generate the skill transfer report."""

    # Scan all repositories
    all_skills_by_name = {}
    repo_skills = {}

    for repo_name in [".claude", ".gemini", ".agents"]:
        skills = scan_repository(project_path, repo_name)
        repo_skills[repo_name] = skills

        for skill_name, skill_info in skills.items():
            if skill_name not in all_skills_by_name:
                all_skills_by_name[skill_name] = []
            all_skills_by_name[skill_name].append(skill_info)

    # Classify
    auto_resolvable_names, auto_resolvable, conflicts = find_conflicts(all_skills_by_name)

    # Count synced vs new for dest repos
    synced_count = 0
    new_count = 0

    for skill_name in auto_resolvable_names:
        skill_list = auto_resolvable[skill_name]
        # Check if it's in source and at least one dest
        in_source = any(s.repo == source_repo for s in skill_list)
        in_dest = any(s.repo in dest_repos for s in skill_list)

        if in_source and in_dest:
            synced_count += 1
        elif in_source:
            new_count += 1

    total_discovered = len(all_skills_by_name)
    total_auto_resolvable = len(auto_resolvable)
    total_conflicts = len(conflicts)

    # Build report
    lines = []
    lines.append("# Skill Transfer Report")
    lines.append(f"Scope: {source_repo}/skills → {', '.join(dest_repos)}/skills | Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append("━" * 70)
    lines.append("SUMMARY")
    lines.append("━" * 70)
    lines.append("")
    lines.append(f"Total skills discovered: {total_discovered}")
    lines.append(f"Auto-resolvable: {total_auto_resolvable} ({synced_count} synced, {new_count} new)")
    lines.append(f"Conflicts requiring decision: {total_conflicts}")
    lines.append("")

    total_dest_after = len(repo_skills.get(dest_repos[0], {})) + new_count
    lines.append(f"After transfer: {dest_repos[0]}/skills/ will have {total_dest_after} skills (+{new_count} new)")
    lines.append("")

    # Auto-resolvable section
    if total_auto_resolvable > 0:
        lines.append("━" * 70)
        lines.append(f"✓ AUTO-RESOLVABLE ({total_auto_resolvable} SKILLS)")
        lines.append("━" * 70)
        lines.append("")

        # Synced
        synced_skills = []
        new_skills = []

        for skill_name in auto_resolvable_names:
            skill_list = auto_resolvable[skill_name]
            in_source = any(s.repo == source_repo for s in skill_list)
            in_dest = any(s.repo in dest_repos for s in skill_list)

            if in_source and in_dest:
                synced_skills.append(skill_name)
            elif in_source:
                new_skills.append(skill_name)

        if synced_skills:
            lines.append("Synced (identical in both):")
            # Format as comma-separated, wrapped at 70 chars
            formatted = "  " + ", ".join(synced_skills)
            for i in range(0, len(formatted), 70):
                lines.append(formatted[i:i+70])
            lines.append("")

        if new_skills:
            lines.append(f"New to {dest_repos[0]} (from {source_repo}):")
            formatted = "  " + ", ".join(new_skills)
            for i in range(0, len(formatted), 70):
                lines.append(formatted[i:i+70])
            lines.append("")

    # Conflicts section
    if total_conflicts > 0:
        lines.append("━" * 70)
        lines.append("⚠ CONFLICTS — YOUR DECISION NEEDED ({})".format(total_conflicts))
        lines.append("━" * 70)
        lines.append("")

        for i, (skill_name, skill_list) in enumerate(sorted(conflicts.items()), 1):
            source_skill = next((s for s in skill_list if s.repo == source_repo), None)
            dest_skill = next((s for s in skill_list if s.repo in dest_repos), None)

            lines.append(f"┌─ {i}. {skill_name}")

            if source_skill:
                version_info = f"v{source_skill.version}" if source_skill.version else "no version"
                lines.append(f"├─ {source_repo}: {version_info} ({source_skill.file_count} files)")

            if dest_skill:
                version_info = f"v{dest_skill.version}" if dest_skill.version else "no version"
                lines.append(f"├─ {dest_repos[0]}: {version_info} ({dest_skill.file_count} files)")

            lines.append(f"└─ Choose: [ ] A) {source_repo}  [ ] B) {dest_repos[0] if dest_skill else 'keep both'}  [ ] C) keep both")
            lines.append("")

    lines.append("━" * 70)
    lines.append("NEXT")
    lines.append("━" * 70)
    lines.append("")
    lines.append(f"Reply with decisions: 1.A 2.B (or similar)")
    lines.append("")

    return "\n".join(lines)


def main():
    import sys

    if len(sys.argv) < 4:
        print("Usage: transfer.py <project_path> <source_repo> <dest_repo1[,dest_repo2,...]>")
        print("Example: transfer.py /path/to/project .claude .gemini,.agents")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    source_repo = sys.argv[2]
    dest_repos = sys.argv[3].split(",")

    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}")
        sys.exit(1)

    report = generate_report(project_path, source_repo, dest_repos)
    print(report)


if __name__ == "__main__":
    main()
