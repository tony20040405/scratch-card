"""客人可以查詢空檔的方案(白名單)。
要新增或調整方案,只改這個檔案。名稱必須與 SimplyBook 後台的服務名稱一致
(空白與全形/半形符號差異會自動忽略)。不在這裡的服務,客人一律查不到。"""
import re
import unicodedata

# (顯示名稱, 客人可能輸入的關鍵字, {"平日"/"假日"/None: SimplyBook 服務名稱})
# None 代表不分平日假日
PLANS = [
    ("入門體驗", ["入門"],
     {None: "入門體驗(全程10分鐘|飛行體驗6分鐘)"}),
    ("沉浸體驗", ["沉浸"],
     {"平日": "沉浸體驗(平日)",
      "假日": "沉浸體驗(全程20分鐘|飛行體驗15分鐘)"}),
    ("熱血飛行", ["熱血"],
     {"平日": "熱血飛行(平日)",
      "假日": "熱血飛行(全程40分鐘|飛行體驗35分鐘)"}),
    ("極限飛行", ["極限"],
     {"平日": "極限飛行(平日)-進階養成 (全程60分鐘)",
      "假日": "極限飛行-進階養成(全程60分鐘)"}),
    ("世界地景", ["世界地景", "地景"],
     {"平日": "世界地景(平日) (全程60分鐘)",
      "假日": "世界地景- (全程60分鐘)"}),
]

WEEKDAY_WORDS = ["平日", "週間", "周間"]
HOLIDAY_WORDS = ["假日", "週末", "周末"]


def norm(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s)).lower()


def parse_query(text: str):
    """回傳 (方案, 平日/假日/None);找不到的項目為 None"""
    t = unicodedata.normalize("NFKC", text)
    day = None
    if any(w in t for w in WEEKDAY_WORDS):
        day = "平日"
    elif any(w in t for w in HOLIDAY_WORDS):
        day = "假日"
    plan = None
    for p in PLANS:
        if p[0] in t or any(k in t for k in p[1]):
            plan = p
            break
    return plan, day


def looks_like_availability(text: str) -> bool:
    """「預約 平日 沉浸體驗」、「平日 沉浸體驗」、「空檔 …」都視為查空檔。
    單純說「預約」(沒有方案與平假日)不算,交給 faq 回覆預約網址。問價格或營業時間的也不算。"""
    if any(k in text for k in ("價", "錢", "費", "營業")):
        return False
    if "空檔" in text:  # 舊關鍵字仍可使用
        return True
    plan, day = parse_query(text)
    if plan is not None:
        return day is not None or "預約" in text
    return "預約" in text and day is not None


MENU = """請輸入「預約 + 平日/假日 + 方案名稱」查詢空檔,例如:
・預約 平日 沉浸體驗
・預約 假日 熱血飛行
・預約 入門體驗(入門體驗不分平假日)

可查詢的方案:入門體驗、沉浸體驗、熱血飛行、極限飛行、世界地景"""

ASK_DAY = "請告知要查「平日」還是「假日」,例如:預約 平日 {name}"
