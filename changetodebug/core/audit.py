"""命中數盤點：算出每條規則在實際 source 中會命中幾處，並建議 expect_count。

要解決的問題：
    old_code 只保證在「產生 profile 當下的那份 source」中唯一。上游後來新增了相似的
    區塊，同一條規則就可能命中多處，而 patcher 是整檔取代所有出現處——它會安靜地把
    好幾個地方一起改掉，記錄裡只寫一句「已修改 N 處」。比對失敗至少會叫，這個不會。

    expect_count 是擋這件事的守門欄位，但要填什麼值只有看過實際 source 才知道。
    這支模組就是去把那個數字量出來。

expect_count 是**逐檔**檢查的（patcher 在單一檔案內比對命中數），所以建議值要看
各檔案的命中數是否一致；不一致就不給建議，交給人判斷。
"""

from collections import Counter
from dataclasses import dataclass, field

from .patcher import normalize_newlines, read_text


@dataclass
class RuleAudit:
    rule_id: str = ""
    label: str = ""
    target: str = ""
    section: str = ""               # modifications / platform_pcd_modifications
    index: int = -1
    regex: bool = False
    files: int = 0                  # 實際找到幾個目標檔
    counts: list = field(default_factory=list)      # 各檔案的命中數
    current: int = 0                # 目前 profile 宣告的 expect_count（0 = 未宣告）
    applied: int = 0                # 已經是套用後狀態的檔案數
    note: str = ""

    @property
    def distinct(self):
        """出現過的非零命中數。"""
        return sorted({c for c in self.counts if c})

    @property
    def suggestion(self):
        """建議的 expect_count；無法給建議時回 0。"""
        if self.regex:
            return 0
        values = self.distinct
        return values[0] if len(values) == 1 else 0

    @property
    def consistent(self):
        return len(self.distinct) <= 1

    @property
    def flagged(self):
        """需要人看一眼的：命中多處、或各檔案不一致。"""
        if self.regex or not self.distinct:
            return False
        return not self.consistent or self.distinct[-1] > 1

    @property
    def status(self):
        if self.regex:
            return "regex 規則，不適用"
        if not self.files:
            return "找不到目標檔"
        if not self.distinct:
            return f"沒有任何檔案命中（{self.applied} 個已是套用後狀態）"
        if not self.consistent:
            return f"各檔案命中數不一致：{Counter(c for c in self.counts if c)}"
        value = self.distinct[0]
        return f"每個檔案各命中 {value} 處" + ("　※ 大於 1" if value > 1 else "")


def audit(profile, base_path, logger, projects=None):
    """對一棵 source tree 盤點每條規則的命中數。純唯讀。"""
    from .tasks.patchset import make_target_resolver

    resolve = make_target_resolver(profile, base_path, logger)
    sections = {"mod": "modifications", "pcd": "platform_pcd_modifications"}
    indexes = {"mod": 0, "pcd": 0, "new": 0}
    results = []

    for rule in profile.all_rules:
        kind = rule.rule_id.split(":")[0] if ":" in rule.rule_id else ""
        index = indexes.get(kind, 0)
        indexes[kind] = index + 1
        if rule.is_new_file or kind not in sections:
            continue

        item = RuleAudit(rule_id=rule.rule_id, label=rule.label,
                         target=rule.target_display, section=sections[kind], index=index,
                         regex=rule.regex, current=rule.expect_count)

        # 多組錨點時，命中數取第一組比對得到的那組；「已套用過」看任一組的 new_code
        variants = [(normalize_newlines(v.old_code), normalize_newlines(v.new_code))
                    for v in rule.variants()]
        for path in resolve(rule):
            if not path.is_file():
                continue
            try:
                text = normalize_newlines(read_text(path)[0])
            except Exception:
                continue
            item.files += 1
            if rule.regex:
                continue
            count = next((text.count(old) for old, _ in variants if old and old in text), 0)
            item.counts.append(count)
            if count == 0 and any(new and new in text for _, new in variants):
                item.applied += 1

        if projects is not None:
            item.note = f"僅統計選中的 {len(projects)} 個專案"
        results.append(item)

    flagged = sum(1 for r in results if r.flagged)
    logger.info(f"盤點完成：{len(results)} 條規則，其中 {flagged} 條需要確認")
    return results
