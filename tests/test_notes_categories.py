"""分类与笔记功能测试：模板树播种、分类树规则、笔记全生命周期、用户隔离。"""

from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, username: str) -> dict:
    client.post("/api/v1/auth/register", json={"username": username, "password": "passw0rd123"})
    tokens = client.post(
        "/api/v1/auth/login", json={"username": username, "password": "passw0rd123"}
    ).json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _find(nodes: list[dict], name: str) -> dict | None:
    for node in nodes:
        if node["name"] == name:
            return node
        hit = _find(node["children"], name)
        if hit is not None:
            return hit
    return None


def _tree(client: TestClient, headers: dict) -> list[dict]:
    return client.get("/api/v1/category/tree", headers=headers).json()["data"]


# ========== 模板分类树 ==========

def test_register_seeds_template_tree(client: TestClient):
    headers = _register_and_login(client, "tree_user")
    tree = _tree(client, headers)

    top_names = [n["name"] for n in tree]
    assert top_names == ["工作", "学习", "技术", "生活", "闪念", "阅读", "三体", "其他"]

    tech = _find(tree, "技术")
    assert [c["name"] for c in tech["children"]] == ["Flutter", "Java", "Nodejs", "Vue"]

    # 模板树最深 3 级：工作/项目文档/XXX服务_V1.0.06
    doc = _find(tree, "XXX服务_V1.0.06")
    assert doc is not None and doc["parent_id"] is not None


# ========== 分类创建与规则 ==========

def test_create_category_and_same_name_conflict(client: TestClient):
    headers = _register_and_login(client, "cat_user")
    work = _find(_tree(client, headers), "工作")

    resp = client.post(
        "/api/v1/category",
        json={"name": "周报", "parent_id": work["id"]},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["parent_id"] == work["id"]
    assert resp.json()["data"]["sort_order"] == 2  # 排在 脚本/项目文档 之后

    resp = client.post(
        "/api/v1/category",
        json={"name": "周报", "parent_id": work["id"]},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == 40904

    # 不同父分类下允许同名
    assert client.post("/api/v1/category", json={"name": "周报"}, headers=headers).status_code == 200


def test_create_category_depth_limit(client: TestClient):
    headers = _register_and_login(client, "depth_user")
    doc = _find(_tree(client, headers), "XXX服务_V1.0.06")  # 已是第 3 级

    resp = client.post(
        "/api/v1/category", json={"name": "再深一层", "parent_id": doc["id"]}, headers=headers
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == 40003


def test_rename_and_soft_delete_promotes_children(client: TestClient):
    headers = _register_and_login(client, "del_user")
    tree = _tree(client, headers)
    work, script = _find(tree, "工作"), _find(tree, "脚本")

    # 重命名
    resp = client.put(
        f"/api/v1/category/{work['id']}", json={"name": "上班"}, headers=headers
    )
    assert resp.json()["data"]["name"] == "上班"

    # 删除父分类 → 活跃子分类提升为顶级
    assert client.delete(f"/api/v1/category/{work['id']}", headers=headers).status_code == 200
    tree = _tree(client, headers)
    assert _find(tree, "上班") is None
    promoted = _find(tree, "脚本")
    assert promoted is not None and promoted["parent_id"] is None
    assert _find(tree, "项目文档") is not None and _find(tree, "项目文档")["parent_id"] is None


def test_move_category_rejects_cycle(client: TestClient):
    headers = _register_and_login(client, "move_user")
    tree = _tree(client, headers)
    work, doc = _find(tree, "工作"), _find(tree, "XXX服务_V1.0.06")

    # 把 工作 移到它自己的子孙 XXX服务_V1.0.06 下 → 成环，拒绝
    resp = client.post(
        f"/api/v1/category/{work['id']}/move",
        json={"parent_id": doc["id"]},
        headers=headers,
    )
    assert resp.status_code == 400


# ========== 笔记生命周期 ==========

def test_note_crud_flow(client: TestClient):
    headers = _register_and_login(client, "note_user")
    tech = _find(_tree(client, headers), "技术")

    created = client.post(
        "/api/v1/note",
        json={"title": "FastAPI 学习笔记", "content": "# DI\nDepends 很好用",
              "category_id": tech["id"], "tags": ["fastapi", "python"]},
        headers=headers,
    )
    assert created.status_code == 200
    note_id = created.json()["data"]["id"]

    # 列表 + 分类过滤
    listed = client.get("/api/v1/note", headers=headers).json()["data"]
    assert listed["total"] == 1
    assert listed["items"][0]["title"] == "FastAPI 学习笔记"
    assert client.get(
        "/api/v1/note", params={"category_id": tech["id"]}, headers=headers
    ).json()["data"]["total"] == 1

    # 详情含正文
    detail = client.get(f"/api/v1/note/{note_id}", headers=headers).json()["data"]
    assert detail["content"].startswith("# DI")
    assert detail["format"] == "md"

    # 更新：置顶 + 移到未分类
    updated = client.put(
        f"/api/v1/note/{note_id}",
        json={"is_pinned": True, "category_id": None},
        headers=headers,
    ).json()["data"]
    assert updated["is_pinned"] is True and updated["category_id"] is None

    # 未分类过滤
    assert client.get(
        "/api/v1/note", params={"uncategorized": True}, headers=headers
    ).json()["data"]["total"] == 1


def test_note_keyword_filter(client: TestClient):
    headers = _register_and_login(client, "kw_user")
    client.post("/api/v1/note", json={"title": "Redis 锁定机制", "content": "INCR 计数"}, headers=headers)
    client.post("/api/v1/note", json={"title": "今日食谱", "content": "西红柿炒鸡蛋"}, headers=headers)

    hit = client.get("/api/v1/note", params={"keyword": "redis"}, headers=headers).json()["data"]
    assert hit["total"] == 1 and hit["items"][0]["title"] == "Redis 锁定机制"


def test_note_trash_restore_permanent(client: TestClient):
    headers = _register_and_login(client, "trash_user")
    note_id = client.post(
        "/api/v1/note", json={"title": "待删笔记", "content": "x"}, headers=headers
    ).json()["data"]["id"]

    # 软删除：列表消失，回收站出现
    client.delete(f"/api/v1/note/{note_id}", headers=headers)
    assert client.get("/api/v1/note", headers=headers).json()["data"]["total"] == 0
    bin_items = client.get("/api/v1/note/recycle-bin", headers=headers).json()["data"]
    assert len(bin_items) == 1 and bin_items[0]["id"] == note_id

    # 恢复
    client.post(f"/api/v1/note/{note_id}/restore", headers=headers)
    assert client.get("/api/v1/note", headers=headers).json()["data"]["total"] == 1

    # 彻底删除：回收站也消失
    client.delete(f"/api/v1/note/{note_id}", headers=headers)
    client.delete(f"/api/v1/note/{note_id}/permanent", headers=headers)
    assert client.get("/api/v1/note/recycle-bin", headers=headers).json()["data"] == []


def test_category_delete_unties_notes(client: TestClient):
    headers = _register_and_login(client, "untie_user")
    tech = _find(_tree(client, headers), "技术")
    note_id = client.post(
        "/api/v1/note",
        json={"title": "挂载笔记", "content": "c", "category_id": tech["id"]},
        headers=headers,
    ).json()["data"]["id"]

    client.delete(f"/api/v1/category/{tech['id']}", headers=headers)
    detail = client.get(f"/api/v1/note/{note_id}", headers=headers).json()["data"]
    assert detail["category_id"] is None  # 笔记变未分类，而不是被连带删除


# ========== 用户隔离 ==========

def test_cross_user_isolation(client: TestClient):
    headers_a = _register_and_login(client, "owner_user")
    headers_b = _register_and_login(client, "stranger_user")

    tech_a = _find(_tree(client, headers_a), "技术")
    note_id = client.post(
        "/api/v1/note",
        json={"title": "私密笔记", "content": "secret", "category_id": tech_a["id"]},
        headers=headers_a,
    ).json()["data"]["id"]

    # B 看不到 A 的笔记与分类（404 而不是 403，不暴露存在性）
    assert client.get(f"/api/v1/note/{note_id}", headers=headers_b).status_code == 404
    assert client.put(f"/api/v1/note/{note_id}", json={"title": "偷改"}, headers=headers_b).status_code == 404
    assert client.delete(f"/api/v1/note/{note_id}", headers=headers_b).status_code == 404
    b_tree = _tree(client, headers_b)
    assert _find(b_tree, "技术")["id"] != tech_a["id"]  # 各自播种的模板树，ID 不同


def test_pinned_note_sorts_first(client: TestClient):
    headers = _register_and_login(client, "pin_user")
    id1 = client.post("/api/v1/note", json={"title": "早", "content": "1"}, headers=headers).json()["data"]["id"]
    client.post("/api/v1/note", json={"title": "晚", "content": "2"}, headers=headers)

    client.put(f"/api/v1/note/{id1}", json={"is_pinned": True}, headers=headers)
    items = client.get("/api/v1/note", headers=headers).json()["data"]["items"]
    assert items[0]["title"] == "早"


# ========== 分类回收站 / 恢复 / 重排 / 合并 ==========

def test_category_recycle_restore_ancestors(client: TestClient):
    headers = _register_and_login(client, "cat_restore")
    work = _find(_tree(client, headers), "工作")
    script = _find(_tree(client, headers), "脚本")
    # 先删子再删父：子分类仍挂在已删父节点上，恢复时必须拉回祖先
    client.delete(f"/api/v1/category/{script['id']}", headers=headers)
    client.delete(f"/api/v1/category/{work['id']}", headers=headers)

    bin_data = client.get("/api/v1/category/recycle-bin", headers=headers).json()["data"]
    ids = {item["id"] for item in bin_data["categories"]}
    assert work["id"] in ids and script["id"] in ids

    restored = client.post(f"/api/v1/category/{script['id']}/restore", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["data"]["restored_count"] >= 2
    tree = _tree(client, headers)
    assert _find(tree, "工作") is not None
    assert _find(tree, "脚本") is not None


def test_category_permanent_delete_and_cleanup(client: TestClient):
    headers = _register_and_login(client, "cat_perm")
    flash = _find(_tree(client, headers), "闪念")
    client.delete(f"/api/v1/category/{flash['id']}", headers=headers)
    wiped = client.delete(f"/api/v1/category/{flash['id']}/permanent", headers=headers)
    assert wiped.status_code == 200
    bin_data = client.get("/api/v1/category/recycle-bin", headers=headers).json()["data"]
    assert all(item["id"] != flash["id"] for item in bin_data["categories"])

    other = _find(_tree(client, headers), "其他")
    client.delete(f"/api/v1/category/{other['id']}", headers=headers)
    from datetime import datetime, timedelta
    import asyncio
    from app.models.category import NoteCategory
    from app.services.category_service import cleanup_expired_categories
    from sqlalchemy import select

    async def _age_and_clean():
        factory = client.app.state.db_session_factory
        async with factory() as db:
            cat = (
                await db.execute(select(NoteCategory).where(NoteCategory.id == other["id"]))
            ).scalar_one()
            cat.deleted_at = datetime.now() - timedelta(days=15)
            await db.commit()
        async with factory() as db:
            count = await cleanup_expired_categories(db, days=14)
            await db.commit()
            return count

    assert asyncio.run(_age_and_clean()) >= 1
    leftover = client.get("/api/v1/category/recycle-bin", headers=headers).json()["data"]
    assert all(item["id"] != other["id"] for item in leftover["categories"])


def test_category_reorder_and_merge(client: TestClient):
    headers = _register_and_login(client, "cat_merge")
    tree = _tree(client, headers)
    top_ids = [n["id"] for n in tree]
    reversed_ids = list(reversed(top_ids))
    resp = client.post(
        "/api/v1/category/reorder",
        json={"parent_id": None, "ordered_ids": reversed_ids},
        headers=headers,
    )
    assert resp.status_code == 200
    names = [n["name"] for n in _tree(client, headers)]
    assert names == list(reversed(["工作", "学习", "技术", "生活", "闪念", "阅读", "三体", "其他"]))

    learning = _find(_tree(client, headers), "学习")
    reading = _find(_tree(client, headers), "阅读")
    merged = client.post(
        "/api/v1/category/batch",
        json={
            "category_ids": [reading["id"]],
            "operation": "merge",
            "merge_target_id": learning["id"],
        },
        headers=headers,
    )
    assert merged.status_code == 200
    assert merged.json()["data"]["merged_count"] == 1
    tree = _tree(client, headers)
    assert _find(tree, "阅读") is None
    assert _find(tree, "学习") is not None
    bin_ids = {c["id"] for c in client.get("/api/v1/category/recycle-bin", headers=headers).json()["data"]["categories"]}
    assert reading["id"] in bin_ids


# ========== 笔记进阶：format / 移动 / 批量 / 过期清理 ==========

def test_note_format_txt_and_move_category(client: TestClient):
    headers = _register_and_login(client, "fmt_user")
    tech = _find(_tree(client, headers), "技术")
    created = client.post(
        "/api/v1/note",
        json={"title": "草稿", "content": "plain text", "format": "txt", "category_id": tech["id"]},
        headers=headers,
    )
    assert created.status_code == 200
    note_id = created.json()["data"]["id"]
    assert created.json()["data"]["format"] == "txt"

    detail = client.get(f"/api/v1/note/{note_id}", headers=headers).json()["data"]
    assert detail["format"] == "txt"

    # 更新接口不能改 format
    client.put(f"/api/v1/note/{note_id}", json={"title": "草稿2", "format": "md"}, headers=headers)
    assert client.get(f"/api/v1/note/{note_id}", headers=headers).json()["data"]["format"] == "txt"

    moved = client.put(
        f"/api/v1/note/{note_id}/category",
        json={"category_id": None},
        headers=headers,
    )
    assert moved.status_code == 200
    assert moved.json()["data"]["category_id"] is None

    assert client.post(
        "/api/v1/note",
        json={"title": "坏类型", "content": "x", "format": "pdf"},
        headers=headers,
    ).status_code == 422


def test_note_batch_and_cleanup(client: TestClient):
    headers = _register_and_login(client, "batch_user")
    learning = _find(_tree(client, headers), "学习")
    id1 = client.post("/api/v1/note", json={"title": "A", "content": "1"}, headers=headers).json()["data"]["id"]
    id2 = client.post("/api/v1/note", json={"title": "B", "content": "2"}, headers=headers).json()["data"]["id"]
    id3 = client.post("/api/v1/note", json={"title": "C", "content": "3"}, headers=headers).json()["data"]["id"]

    pinned = client.post(
        "/api/v1/note/batch",
        json={"note_ids": [id1], "operation": "pin"},
        headers=headers,
    )
    assert pinned.status_code == 200
    assert client.get(f"/api/v1/note/{id1}", headers=headers).json()["data"]["is_pinned"] is True

    moved = client.post(
        "/api/v1/note/batch",
        json={"note_ids": [id1, id2], "operation": "move", "target_category_id": learning["id"]},
        headers=headers,
    )
    assert moved.json()["data"]["success_count"] == 2
    assert client.get(f"/api/v1/note/{id1}", headers=headers).json()["data"]["category_id"] == learning["id"]

    deleted = client.post(
        "/api/v1/note/batch",
        json={"note_ids": [id2, id3], "operation": "delete"},
        headers=headers,
    )
    assert deleted.json()["data"]["success_count"] == 2
    bin_items = client.get("/api/v1/note/recycle-bin", headers=headers).json()["data"]
    assert {item["id"] for item in bin_items} >= {id2, id3}
    assert all("days_remaining" in item for item in bin_items)

    restored = client.post(
        "/api/v1/note/batch",
        json={"note_ids": [id2], "operation": "restore"},
        headers=headers,
    )
    assert restored.json()["data"]["success_count"] == 1

    wiped = client.post(
        "/api/v1/note/batch",
        json={"note_ids": [id3], "operation": "permanent_delete"},
        headers=headers,
    )
    assert wiped.json()["data"]["success_count"] == 1
    leftover = client.get("/api/v1/note/recycle-bin", headers=headers).json()["data"]
    assert all(item["id"] != id3 for item in leftover)

    doomed = client.post(
        "/api/v1/note", json={"title": "过期", "content": "x"}, headers=headers
    ).json()["data"]["id"]
    client.delete(f"/api/v1/note/{doomed}", headers=headers)

    from datetime import datetime, timedelta
    import asyncio
    from app.models.note import Note
    from app.services.note_service import cleanup_expired_notes
    from sqlalchemy import select

    async def _age_and_clean():
        factory = client.app.state.db_session_factory
        async with factory() as db:
            note = (await db.execute(select(Note).where(Note.id == doomed))).scalar_one()
            note.deleted_at = datetime.now() - timedelta(days=15)
            await db.commit()
        async with factory() as db:
            count = await cleanup_expired_notes(db, days=14)
            await db.commit()
            return count

    assert asyncio.run(_age_and_clean()) >= 1
    leftover = client.get("/api/v1/note/recycle-bin", headers=headers).json()["data"]
    assert all(item["id"] != doomed for item in leftover)


# ========== 笔记关键词搜索 ==========

def test_note_keyword_search_title_outranks_content(client: TestClient):
    headers = _register_and_login(client, "search_user")
    title_id = client.post(
        "/api/v1/note",
        json={"title": "Redis 笔记", "content": "随便写点"},
        headers=headers,
    ).json()["data"]["id"]
    content_id = client.post(
        "/api/v1/note",
        json={"title": "缓存策略", "content": "用 Redis 做锁定"},
        headers=headers,
    ).json()["data"]["id"]
    deleted_id = client.post(
        "/api/v1/note",
        json={"title": "Redis 回收", "content": "x"},
        headers=headers,
    ).json()["data"]["id"]
    client.delete(f"/api/v1/note/{deleted_id}", headers=headers)

    # 通配符按字面匹配，不会把所有笔记搜出来
    wild = client.post(
        "/api/v1/note/search",
        json={"query": "%", "top_k": 20},
        headers=headers,
    )
    assert wild.status_code == 200
    assert wild.json()["data"]["results"] == []

    resp = client.post(
        "/api/v1/note/search",
        json={"query": "Redis", "top_k": 20},
        headers=headers,
    )
    assert resp.status_code == 200
    payload = resp.json()["data"]
    ids = [hit["note"]["id"] for hit in payload["results"]]
    scores = {hit["note"]["id"]: hit["score"] for hit in payload["results"]}
    assert title_id in ids and content_id in ids
    assert deleted_id not in ids
    assert ids.index(title_id) < ids.index(content_id)
    assert scores[title_id] == 1.0
    assert scores[content_id] == 0.5

    other = _register_and_login(client, "search_stranger")
    isolated = client.post(
        "/api/v1/note/search",
        json={"query": "Redis"},
        headers=other,
    ).json()["data"]["results"]
    assert isolated == []


# ========== 笔记模板 ==========

def test_note_template_crud_apply_and_isolation(client: TestClient):
    headers = _register_and_login(client, "tpl_user")
    created = client.post(
        "/api/v1/note-template",
        json={
            "name": "会议纪要",
            "content_structure": {"markdown": "## 议题\n\n- \n"},
            "category": "工作",
        },
        headers=headers,
    )
    assert created.status_code == 200
    tid = created.json()["data"]["id"]
    assert created.json()["data"]["name"] == "会议纪要"

    listed = client.get("/api/v1/note-template", headers=headers).json()["data"]["templates"]
    assert any(item["id"] == tid for item in listed)

    client.put(
        f"/api/v1/note-template/{tid}",
        json={"name": "周会纪要"},
        headers=headers,
    )
    detail = client.get(f"/api/v1/note-template/{tid}", headers=headers).json()["data"]
    assert detail["name"] == "周会纪要"

    applied = client.post(
        f"/api/v1/note-template/{tid}/apply",
        json={},
        headers=headers,
    )
    assert applied.status_code == 200
    note_id = applied.json()["data"]["id"]
    note = client.get(f"/api/v1/note/{note_id}", headers=headers).json()["data"]
    assert note["title"] == "周会纪要"
    assert "## 议题" in note["content"]

    stranger = _register_and_login(client, "tpl_stranger")
    assert client.get(f"/api/v1/note-template/{tid}", headers=stranger).status_code == 404
    assert client.post(f"/api/v1/note-template/{tid}/apply", json={}, headers=stranger).status_code == 404

    assert client.delete(f"/api/v1/note-template/{tid}", headers=headers).status_code == 200
    assert client.get(f"/api/v1/note-template/{tid}", headers=headers).status_code == 404


# ========== 笔记 AI 辅助 ==========

def test_note_ai_assist_uses_injected_fn(client: TestClient, monkeypatch):
    from app.services import note_ai_service

    async def fake_complete(prompt: str) -> str:
        if "补全" in prompt:
            return "接下来写测试用例。"
        if "标签" in prompt:
            return "fastapi, 测试, pytest"
        if "扩写" in prompt:
            return "扩写后的段落。"
        return "续写后的段落。"

    monkeypatch.setattr(note_ai_service, "set_note_ai_fn", note_ai_service.set_note_ai_fn)
    note_ai_service.set_note_ai_fn(fake_complete)
    headers = _register_and_login(client, "ai_note_user")

    auto = client.post(
        "/api/v1/note/autocomplete",
        json={"content": "先写接口。", "cursor_position": 5},
        headers=headers,
    )
    assert auto.status_code == 200
    assert "测试用例" in auto.json()["data"]["completion"]

    write = client.post(
        "/api/v1/note/write-assistant",
        json={"content": "先写接口。", "mode": "expand"},
        headers=headers,
    )
    assert write.json()["data"]["result"] == "扩写后的段落。"

    tags = client.post(
        "/api/v1/note/auto-tag",
        json={"title": "FastAPI", "content": "Depends 很好用"},
        headers=headers,
    )
    assert tags.json()["data"]["tags"] == ["fastapi", "测试", "pytest"]

    empty = client.post(
        "/api/v1/note/write-assistant",
        json={"content": "x", "mode": "rewrite"},
        headers=headers,
    )
    assert empty.status_code == 422
