//! 龙胤立志传 - Web 存档修改器 (Rust 版)
//!
//! 用 Rust 重构 web_server.py，替代 Flask 后端，单文件绿色客户端：
//! - 手写极简 HTTP 服务器 (std::net)，每连接一线程
//! - serde_json 处理任意嵌套存档 JSON
//! - 前端 (index.html / world.html) 与数据映射 (skill/talent/tag/spe) 全部 include_bytes 内嵌
//! - 不依赖任何外部资源文件
//! 编译目标：release 可执行文件 < 800KB。
#![recursion_limit = "256"]

use serde_json::{json, Map, Value};
use std::collections::BTreeMap;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::Path;
use std::sync::{Mutex, OnceLock};
use std::time::Duration;

// ========== 内嵌资源 (压缩存储, 运行时解压) ==========

const INDEX_BIN: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/index.bin"));
const WORLD_BIN: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/world.bin"));
const SKILL_BIN: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/skill.bin"));
const TAG_BIN: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/tag.bin"));
// 小文件直接内嵌
const SPE_ATTR_MAP_JSON: &str = include_str!("../assets/spe_attr_map.json");
const TALENT_NAMES_JSON: &str = include_str!("../assets/talent_names.json");

fn inflate_str(data: &[u8]) -> String {
    let out = miniz_oxide::inflate::decompress_to_vec(data).unwrap_or_default();
    String::from_utf8_lossy(&out).into_owned()
}

static INDEX_HTML: OnceLock<String> = OnceLock::new();
static WORLD_HTML: OnceLock<String> = OnceLock::new();

fn index_html() -> &'static str {
    INDEX_HTML.get_or_init(|| inflate_str(INDEX_BIN)).as_str()
}

fn world_html() -> &'static str {
    WORLD_HTML.get_or_init(|| inflate_str(WORLD_BIN)).as_str()
}

// ========== 常量定义 ==========

const DEFAULT_SAVE_FOLDER: &str =
    r"C:\Program Files (x86)\Steam\steamapps\common\LongYinLiZhiZhuan\LongYinLiZhiZhuan_Data\Save";

fn force_name(id: i64) -> String {
    let name = match id {
        -1 => "无",
        0 => "无",
        1 => "少林派",
        2 => "武当派",
        3 => "峨眉派",
        4 => "丐帮",
        5 => "华山派",
        6 => "衡山派",
        7 => "青城派",
        8 => "点苍派",
        9 => "昆仑派",
        10 => "崆峒派",
        11 => "天山派",
        12 => "雪山派",
        13 => "点星阁",
        14 => "五毒教",
        15 => "明教",
        16 => "日月神教",
        17 => "红花会",
        18 => "天地会",
        19 => "六扇门",
        20 => "锦衣卫",
        21 => "东厂",
        22 => "西厂",
        23 => "大理段氏",
        24 => "全真教",
        25 => "仙霞派",
        26 => "茅山派",
        27 => "桃花岛",
        28 => "逍遥派",
        29 => "灵鹫宫",
        _ => return format!("未知({})", id),
    };
    name.to_string()
}

fn nature_name(id: i64) -> String {
    let name = match id {
        0 => "仁善",
        1 => "正直",
        2 => "刚正",
        3 => "忠义",
        4 => "稳妥",
        5 => "温和",
        6 => "平常",
        7 => "狡黠",
        8 => "乖张",
        9 => "叛逆",
        10 => "唯我",
        11 => "冷酷",
        _ => return "未知".to_string(),
    };
    name.to_string()
}

const ITEM_TYPES: [&str; 11] = [
    "武器", "护甲", "头盔", "鞋子", "饰品", "药品", "坐骑", "秘籍", "材料", "宝物", "杂项",
];

fn item_type_name(t: i64) -> String {
    if (0..11).contains(&t) {
        ITEM_TYPES[t as usize].to_string()
    } else {
        "未知".to_string()
    }
}

fn favor_status(favor: f64) -> (&'static str, &'static str) {
    if favor == -999999.0 {
        ("unknown", "未知")
    } else if favor >= 80.0 {
        ("love", "挚爱")
    } else if favor >= 60.0 {
        ("close", "亲密")
    } else if favor >= 40.0 {
        ("friendly", "友善")
    } else if favor >= 20.0 {
        ("neutral_positive", "略有好感")
    } else if favor >= 0.0 {
        ("neutral", "中立")
    } else if favor >= -20.0 {
        ("neutral_negative", "略有不悦")
    } else if favor >= -40.0 {
        ("dislike", "厌恶")
    } else if favor >= -60.0 {
        ("hate", "憎恨")
    } else if favor >= -80.0 {
        ("enemy", "仇敌")
    } else {
        ("nemesis", "死敌")
    }
}

// ========== 全局状态 ==========

struct State {
    hero_data: Option<Vec<Value>>,
    hero_filepath: String,
    save_data: Option<Value>,
    save_filepath: String,
    save_folder: Option<String>,
    skill_names: BTreeMap<i64, Value>,
    spe_attr_map: BTreeMap<String, String>,
    talent_names: BTreeMap<i64, Value>,
    tag_names: BTreeMap<i64, Value>,
}

static STATE: OnceLock<Mutex<State>> = OnceLock::new();

// ========== 数值工具 ==========

fn v_f64(v: &Value) -> f64 {
    match v {
        Value::Number(n) => n.as_f64().unwrap_or(0.0),
        Value::String(s) => s.parse::<f64>().unwrap_or(0.0),
        Value::Bool(b) => {
            if *b {
                1.0
            } else {
                0.0
            }
        }
        _ => 0.0,
    }
}

fn v_i64(v: &Value) -> i64 {
    match v {
        Value::Number(n) => n.as_i64().unwrap_or(0),
        Value::String(s) => s.parse::<i64>().unwrap_or(0),
        Value::Bool(b) => {
            if *b {
                1
            } else {
                0
            }
        }
        _ => 0,
    }
}

fn v_bool(v: &Value) -> bool {
    v.as_bool().unwrap_or(false)
}

fn get_str<'a>(v: &'a Value, key: &str, default: &'a str) -> &'a str {
    v.get(key).and_then(|x| x.as_str()).unwrap_or(default)
}

fn field_or(v: &Value, key: &str, default: Value) -> Value {
    v.get(key).cloned().unwrap_or(default)
}

// ========== 名称查询 ==========

fn name_from_map(map: &BTreeMap<i64, Value>, id: &Value, prefix: &str) -> String {
    if let Value::Number(n) = id {
        if let Some(i) = n.as_i64() {
            if let Some(info) = map.get(&i) {
                if let Some(name) = info.get("name").and_then(|x| x.as_str()) {
                    return name.to_string();
                }
            }
            return format!("{}({})", prefix, i);
        }
    }
    format!("{}", prefix)
}

fn get_skill_name(state: &State, sid: &Value) -> String {
    name_from_map(&state.skill_names, sid, "未知")
}

fn get_talent_name(state: &State, tid: &Value) -> String {
    name_from_map(&state.talent_names, tid, "未知")
}

fn get_tag_name(state: &State, tid: &Value) -> String {
    name_from_map(&state.tag_names, tid, "未知")
}

fn get_spe_attr_name(state: &State, attr_id: &str) -> String {
    state
        .spe_attr_map
        .get(attr_id)
        .cloned()
        .unwrap_or_else(|| format!("属性{}", attr_id))
}

fn find_hero_idx(arr: &[Value], id: i64) -> Option<usize> {
    arr.iter()
        .position(|h| h.get("heroID").and_then(|v| v.as_i64()) == Some(id))
}

// ========== 数据修改函数 ==========

fn set_arr_f(hero: &mut Value, key: &str, idx: usize, v: f64) -> bool {
    match hero.get_mut(key).and_then(|x| x.as_array_mut()) {
        Some(a) if idx < a.len() => {
            a[idx] = json!(v);
            true
        }
        _ => false,
    }
}

fn modify_status(hero: &mut Value, hp: Option<f64>, power: Option<f64>, mana: Option<f64>) {
    if let Some(v) = hp {
        hero["hp"] = json!(v);
        hero["maxhp"] = json!(v);
        hero["realMaxHp"] = json!(v);
    }
    if let Some(v) = power {
        hero["power"] = json!(v);
        hero["maxPower"] = json!(v);
        hero["realMaxPower"] = json!(v);
    }
    if let Some(v) = mana {
        hero["mana"] = json!(v);
        hero["maxMana"] = json!(v);
        hero["realMaxMana"] = json!(v);
    }
}

fn modify_fame(hero: &mut Value, fame: Option<f64>, bad_fame: Option<f64>) {
    if let Some(v) = fame {
        hero["fame"] = json!(v);
    }
    if let Some(v) = bad_fame {
        hero["badFame"] = json!(v);
    }
}

fn ensure_item_list(hero: &mut Value) {
    if !hero.get("itemListData").map(|v| v.is_object()).unwrap_or(false) {
        hero["itemListData"] = json!({"money": 0, "weight": 0, "maxWeight": 100, "allItem": []});
    }
}

fn modify_money(hero: &mut Value, money: i64) {
    ensure_item_list(hero);
    if let Some(ild) = hero.get_mut("itemListData") {
        ild["money"] = json!(money);
    }
}

fn add_item(hero: &mut Value, item: Value) {
    ensure_item_list(hero);
    if let Some(ild) = hero.get_mut("itemListData") {
        if !ild.get("allItem").map(|v| v.is_array()).unwrap_or(false) {
            ild["allItem"] = json!([]);
        }
        let w = v_f64(item.get("weight").unwrap_or(&json!(0)));
        if let Some(all) = ild.get_mut("allItem").and_then(|v| v.as_array_mut()) {
            all.push(item);
        }
        let cur_w = v_f64(ild.get("weight").unwrap_or(&json!(0)));
        ild["weight"] = json!(cur_w + w);
    }
}

fn remove_item(hero: &mut Value, idx: usize) -> Option<Value> {
    let ild = hero.get_mut("itemListData")?;
    let items = ild.get_mut("allItem")?.as_array_mut()?;
    if idx >= items.len() {
        return None;
    }
    let removed = items.remove(idx);
    let w = v_f64(removed.get("weight").unwrap_or(&json!(0)));
    let cur_w = v_f64(ild.get("weight").unwrap_or(&json!(0)));
    ild["weight"] = json!(cur_w - w);
    Some(removed)
}

fn add_skill(hero: &mut Value, skill_id: Value, lv: Value) {
    let belong_hero_id = hero.get("heroID").cloned().unwrap_or(Value::Null);
    let new_skill = json!({
        "skillID": skill_id,
        "lv": lv,
        "fightExp": 0.0,
        "bookExp": 0.0,
        "equiped": false,
        "isNew": true,
        "belongHeroID": belong_hero_id,
        "speEquipData": {"heroSpeAddData": {}},
        "equipUseSpeAddValue": 0.0,
        "speUseData": {"heroSpeAddData": {}},
        "damageUseSpeAddValue": 0.0,
        "selfUseSpeAddValue": 0.0,
        "enemyUseSpeAddValue": 0.0,
        "extraAddData": {"heroSpeAddData": {}},
        "maxManaChanged": false,
    });
    if let Some(arr) = hero.get_mut("kungfuSkills").and_then(|v| v.as_array_mut()) {
        arr.push(new_skill);
    } else {
        hero["kungfuSkills"] = json!([new_skill]);
    }
}

fn all_skills_max(hero: &mut Value, lv: i64, damage: f64) {
    if let Some(arr) = hero.get_mut("kungfuSkills").and_then(|v| v.as_array_mut()) {
        for skill in arr {
            skill["lv"] = json!(lv);
            skill["damageUseSpeAddValue"] = json!(damage);
        }
    }
}

fn remove_skill(hero: &mut Value, idx: usize) -> Option<Value> {
    let arr = hero.get_mut("kungfuSkills")?.as_array_mut()?;
    if idx >= arr.len() {
        return None;
    }
    let removed = arr.remove(idx);
    for field in ["internalSkillSaveRecord", "dodgeSkillSaveRecord", "uniqueSkillSaveRecord"] {
        if let Some(v) = hero.get_mut(field) {
            if let Some(val) = v.as_i64() {
                if val as usize == idx {
                    *v = json!(-1);
                } else if val > idx as i64 {
                    *v = json!(val - 1);
                }
            }
        }
    }
    if let Some(records) = hero
        .get_mut("attackSkillSaveRecord")
        .and_then(|v| v.as_array_mut())
    {
        for v in records.iter_mut() {
            if let Some(val) = v.as_i64() {
                if val as usize == idx {
                    *v = json!(-1);
                } else if val > idx as i64 {
                    *v = json!(val - 1);
                }
            }
        }
    }
    Some(removed)
}

fn heal_hero(hero: &mut Value) {
    hero["hp"] = hero.get("maxhp").cloned().unwrap_or(json!(999));
    hero["power"] = hero.get("maxPower").cloned().unwrap_or(json!(999));
    hero["mana"] = hero.get("maxMana").cloned().unwrap_or(json!(999));
    hero["internalInjury"] = json!(0.0);
    hero["externalInjury"] = json!(0.0);
    hero["poisonInjury"] = json!(0.0);
}

fn revive_hero(hero: &mut Value) {
    hero["dead"] = json!(false);
    heal_hero(hero);
}

fn max_all_attrs(hero: &mut Value, value: f64) {
    for i in 0..6 {
        set_arr_f(hero, "baseAttri", i, value);
        set_arr_f(hero, "totalAttri", i, value);
        set_arr_f(hero, "maxAttri", i, value);
    }
    for i in 0..9 {
        set_arr_f(hero, "baseFightSkill", i, value);
        set_arr_f(hero, "totalFightSkill", i, value);
        set_arr_f(hero, "maxFightSkill", i, value);
        set_arr_f(hero, "baseLivingSkill", i, value);
        set_arr_f(hero, "totalLivingSkill", i, value);
        set_arr_f(hero, "maxLivingSkill", i, value);
    }
    modify_status(hero, Some(value), Some(value), Some(value));
}

fn modify_favor(hero: &mut Value, value: f64) {
    if value == -999999.0 {
        hero["favor"] = json!(-999999.0);
    } else {
        hero["favor"] = json!(value.clamp(-100.0, 100.0));
    }
}

fn list_add(hero: &mut Value, key: &str, id: i64) {
    let ids = hero.get_mut(key).and_then(|v| v.as_array_mut());
    match ids {
        Some(arr) => {
            let exists = arr.iter().any(|v| v.as_i64() == Some(id));
            if !exists {
                arr.push(json!(id));
            }
        }
        None => hero[key] = json!([id]),
    }
}

fn list_remove(hero: &mut Value, key: &str, id: i64) {
    if let Some(arr) = hero.get_mut(key).and_then(|v| v.as_array_mut()) {
        arr.retain(|v| v.as_i64() != Some(id));
    }
}

fn parse_spe_data_array(state: &State, data: &Value) -> Vec<Value> {
    let mut out = Vec::new();
    if let Some(map) = data.as_object() {
        for (k, v) in map {
            out.push(json!({"id": k, "name": get_spe_attr_name(state, k), "value": v}));
        }
    }
    out
}

fn parse_spe_data_map(data: &Value) -> Value {
    let mut map = Map::new();
    if let Some(m) = data.as_object() {
        for (k, v) in m {
            map.insert(k.clone(), v.clone());
        }
    }
    Value::Object(map)
}

// ========== 字段应用辅助 (Save PUT) ==========

#[derive(Clone, Copy)]
enum FT {
    I,
    F,
    B,
    FL,
}

fn apply_field(obj: &mut Value, body: &Value, key: &str, t: FT) {
    let Some(v) = body.get(key) else { return };
    obj[key] = match t {
        FT::I => json!(v_i64(v)),
        FT::F => json!(v_f64(v)),
        FT::B => json!(v.as_bool().unwrap_or(false)),
        FT::FL => json!(v
            .as_array()
            .map(|a| a.iter().map(v_f64).collect::<Vec<_>>())
            .unwrap_or_default()),
    };
}

// ========== HTTP 解析 ==========

struct Request {
    method: String,
    path: String,
    query: BTreeMap<String, String>,
    body: Vec<u8>,
}

fn find_sub(hay: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() || hay.len() < needle.len() {
        return None;
    }
    hay.windows(needle.len()).position(|w| w == needle)
}

fn url_decode(s: &str) -> String {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(b.len());
    let mut i = 0;
    while i < b.len() {
        match b[i] {
            b'%' if i + 2 < b.len() => {
                let h = (b[i + 1] as char).to_digit(16);
                let l = (b[i + 2] as char).to_digit(16);
                if let (Some(h), Some(l)) = (h, l) {
                    out.push((h * 16 + l) as u8);
                    i += 3;
                } else {
                    out.push(b[i]);
                    i += 1;
                }
            }
            b'+' => {
                out.push(b' ');
                i += 1;
            }
            c => {
                out.push(c);
                i += 1;
            }
        }
    }
    String::from_utf8_lossy(&out).into_owned()
}

fn parse_request(stream: &mut TcpStream) -> Option<Request> {
    let mut buf = Vec::new();
    let mut tmp = [0u8; 8192];
    while find_sub(&buf, b"\r\n\r\n").is_none() {
        let n = stream.read(&mut tmp).ok()?;
        if n == 0 {
            return None;
        }
        buf.extend_from_slice(&tmp[..n]);
        if buf.len() > 20_000_000 {
            return None;
        }
    }
    let head_end = find_sub(&buf, b"\r\n\r\n")? + 4;
    let head = String::from_utf8_lossy(&buf[..head_end]).into_owned();

    let mut lines = head.split("\r\n");
    let request_line = lines.next().unwrap_or("").to_string();
    let mut parts = request_line.split_whitespace();
    let method = parts.next().unwrap_or("GET").to_string();
    let target = parts.next().unwrap_or("/").to_string();

    let mut content_length = 0usize;
    for line in lines {
        if let Some(idx) = line.find(':') {
            let k = line[..idx].trim().to_ascii_lowercase();
            let v = line[idx + 1..].trim();
            if k == "content-length" {
                content_length = v.parse().unwrap_or(0);
            }
        }
    }

    let mut body = buf[head_end..].to_vec();
    let have = body.len();
    if have < content_length {
        let mut rest = vec![0u8; content_length - have];
        let mut read = 0;
        while read < rest.len() {
            let n = stream.read(&mut rest[read..]).ok()?;
            if n == 0 {
                break;
            }
            read += n;
        }
        body.extend_from_slice(&rest[..read]);
    }

    let (path, query_str) = match target.find('?') {
        Some(i) => (&target[..i], &target[i + 1..]),
        None => (target.as_str(), ""),
    };
    let mut query = BTreeMap::new();
    for pair in query_str.split('&') {
        if pair.is_empty() {
            continue;
        }
        let (k, v) = match pair.find('=') {
            Some(i) => (&pair[..i], &pair[i + 1..]),
            None => (pair, ""),
        };
        query.insert(url_decode(k), url_decode(v));
    }

    Some(Request {
        method,
        path: path.to_string(),
        query,
        body,
    })
}

fn body_json(req: &Request) -> Value {
    if req.body.is_empty() {
        return Value::Null;
    }
    serde_json::from_slice(&req.body).unwrap_or(Value::Null)
}

fn json_err(msg: &str) -> Vec<u8> {
    serde_json::to_vec(&json!({"error": msg})).unwrap_or_default()
}

// ========== 响应构造 ==========

fn reason(status: u16) -> &'static str {
    match status {
        200 => "OK",
        204 => "No Content",
        400 => "Bad Request",
        404 => "Not Found",
        405 => "Method Not Allowed",
        500 => "Internal Server Error",
        _ => "",
    }
}

fn build_response(status: u16, content_type: &str, body: &[u8]) -> Vec<u8> {
    let mut resp = Vec::new();
    resp.extend_from_slice(format!("HTTP/1.1 {} {}\r\n", status, reason(status)).as_bytes());
    resp.extend_from_slice(format!("Content-Type: {}\r\n", content_type).as_bytes());
    resp.extend_from_slice(format!("Content-Length: {}\r\n", body.len()).as_bytes());
    resp.extend_from_slice(b"Connection: close\r\n\r\n");
    resp.extend_from_slice(body);
    resp
}

fn json_resp(status: u16, value: &Value) -> (u16, &'static str, Vec<u8>) {
    let body = serde_json::to_vec(value).unwrap_or_default();
    (status, "application/json", body)
}

fn html_resp(status: u16, html: &str) -> (u16, &'static str, Vec<u8>) {
    (
        status,
        "text/html; charset=utf-8",
        html.as_bytes().to_vec(),
    )
}

// ========== 备份时间戳 ==========

#[cfg(windows)]
fn local_timestamp() -> String {
    #[repr(C)]
    struct SystemTime {
        w_year: u16,
        w_month: u16,
        w_day_of_week: u16,
        w_day: u16,
        w_hour: u16,
        w_minute: u16,
        w_second: u16,
        w_milliseconds: u16,
    }
    extern "system" {
        fn GetLocalTime(lp_system_time: *mut SystemTime);
    }
    let mut t = SystemTime {
        w_year: 0,
        w_month: 0,
        w_day_of_week: 0,
        w_day: 0,
        w_hour: 0,
        w_minute: 0,
        w_second: 0,
        w_milliseconds: 0,
    };
    unsafe {
        GetLocalTime(&mut t);
    }
    format!(
        "{:04}{:02}{:02}_{:02}{:02}{:02}",
        t.w_year, t.w_month, t.w_day, t.w_hour, t.w_minute, t.w_second
    )
}

#[cfg(not(windows))]
fn local_timestamp() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0);
    let days = secs.div_euclid(86400);
    let rem = secs.rem_euclid(86400);
    let (h, m, s) = (rem / 3600, (rem % 3600) / 60, rem % 60);
    let z = days + 719468;
    let era = z.div_euclid(146097);
    let doe = z.rem_euclid(146097);
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let mo = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if mo <= 2 { y + 1 } else { y };
    format!("{:04}{:02}{:02}_{:02}{:02}{:02}", y, mo, d, h, m, s)
}

// ========== 工具 ==========

fn with_state<T>(f: impl FnOnce(&mut State) -> T) -> T {
    f(&mut STATE.get().unwrap().lock().unwrap())
}

fn load_data_from_file(filepath: &str) -> Result<Value, String> {
    let s = std::fs::read_to_string(filepath).map_err(|e| format!("读取失败: {}", e))?;
    serde_json::from_str(&s).map_err(|e| format!("JSON解析失败: {}", e))
}

fn find_area<'a>(save: &'a Value, id: i64) -> Option<&'a Value> {
    save.get("Areas")?
        .as_array()?
        .iter()
        .find(|a| a.get("areaID").and_then(|v| v.as_i64()) == Some(id))
}

fn find_force<'a>(save: &'a Value, id: i64) -> Option<&'a Value> {
    save.get("Forces")?
        .as_array()?
        .iter()
        .find(|f| f.get("forceID").and_then(|v| v.as_i64()) == Some(id))
}

// ========== API: 状态 / 文件夹 ==========

fn handle_status() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let loaded = state.hero_data.is_some();
        let hero_count = state.hero_data.as_ref().map(|h| h.len()).unwrap_or(0);
        json_resp(
            200,
            &json!({
                "loaded": loaded,
                "hero_count": hero_count,
                "filepath": state.hero_filepath,
                "save_folder": state.save_folder,
                "save_loaded": state.save_data.is_some(),
            }),
        )
    })
}

fn handle_save_folder(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let folder = body
        .get("folder")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .to_string();
    if folder.is_empty() || !Path::new(&folder).is_dir() {
        return (400, "application/json", json_err("无效的存档文件夹"));
    }
    with_state(|state| {
        state.save_folder = Some(folder.clone());
        json_resp(200, &json!({"success": true, "folder": folder}))
    })
}

fn handle_browse_folders(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let mut path = req
        .query
        .get("path")
        .cloned()
        .unwrap_or_else(|| ".".to_string());
    if path == "." {
        path = std::env::current_dir()
            .map(|p| p.to_string_lossy().into_owned())
            .unwrap_or_else(|_| ".".to_string());
    }
    if !Path::new(&path).exists() {
        return (400, "application/json", json_err("路径不存在"));
    }
    let mut items: Vec<Value> = Vec::new();
    if let Ok(rd) = std::fs::read_dir(&path) {
        let mut names: Vec<String> = Vec::new();
        for entry in rd.flatten() {
            let name = entry.file_name().to_string_lossy().into_owned();
            if entry.path().is_dir() {
                names.push(name);
            }
        }
        names.sort();
        for name in names {
            let full = if path.ends_with('/') || path.ends_with('\\') {
                format!("{}{}", path, name)
            } else {
                format!("{}\\{}", path, name)
            };
            items.push(json!({"name": name, "path": full, "type": "folder"}));
        }
    }
    let parent = if path != "/" {
        Path::new(&path)
            .parent()
            .map(|p| p.to_string_lossy().into_owned())
    } else {
        None
    };
    json_resp(200, &json!({"current": path, "parent": parent, "items": items}))
}

fn handle_save_slots() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save_folder = match &state.save_folder {
            Some(f) => f.clone(),
            None => return (400, "application/json", json_err("请先选择存档文件夹")),
        };
        let mut slots = Vec::new();
        for i in 0..11 {
            let slot_dir = Path::new(&save_folder).join(format!("SaveSlot{}", i));
            let hero_path = slot_dir.join("Hero");
            let info_path = slot_dir.join("Info");
            let name = match i {
                0 => "自动存档".to_string(),
                10 => "快速存档".to_string(),
                _ => format!("存档{}", i),
            };
            let mut info = Value::Null;
            if info_path.is_file() {
                if let Ok(s) = std::fs::read_to_string(&info_path) {
                    info = serde_json::from_str(&s).unwrap_or(Value::Null);
                }
            }
            slots.push(json!({
                "slot": i,
                "name": name,
                "exists": hero_path.exists(),
                "info": info,
            }));
        }
        json_resp(200, &json!(slots))
    })
}

// ========== API: 加载 ==========

fn handle_save_load(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let filepath = match body.get("slot").and_then(|x| x.as_i64()) {
        Some(slot) => {
            let sf = with_state(|s| s.save_folder.clone());
            let sf = match sf {
                Some(f) => f,
                None => return (400, "application/json", json_err("请先选择存档文件夹")),
            };
            let p = Path::new(&sf).join(format!("SaveSlot{}", slot)).join("Save");
            if !p.exists() {
                return (400, "application/json", json_err(&format!("存档槽{}的Save文件不存在", slot)));
            }
            p.to_string_lossy().into_owned()
        }
        None => body
            .get("path")
            .and_then(|x| x.as_str())
            .unwrap_or("Save")
            .to_string(),
    };
    let data = match load_data_from_file(&filepath) {
        Ok(d) => d,
        Err(e) => return (400, "application/json", json_err(&e)),
    };
    with_state(|state| {
        state.save_data = Some(data);
        state.save_filepath = filepath.clone();
        json_resp(200, &json!({"success": true, "filepath": filepath}))
    })
}

fn handle_load(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let slot = body.get("slot").and_then(|x| x.as_i64());
    let filepath: String;
    let mut save_path: Option<String> = None;
    if let Some(slot) = slot {
        let sf = with_state(|s| s.save_folder.clone());
        let sf = match sf {
            Some(f) => f,
            None => return (400, "application/json", json_err("请先选择存档文件夹")),
        };
        let slot_dir = Path::new(&sf).join(format!("SaveSlot{}", slot));
        let hero_path = slot_dir.join("Hero");
        if !hero_path.exists() {
            return (400, "application/json", json_err(&format!("存档槽{}不存在", slot)));
        }
        filepath = hero_path.to_string_lossy().into_owned();
        let sp = slot_dir.join("Save");
        if sp.exists() {
            save_path = Some(sp.to_string_lossy().into_owned());
        }
    } else {
        filepath = body
            .get("path")
            .and_then(|x| x.as_str())
            .unwrap_or("Hero")
            .to_string();
    }

    let data = match load_data_from_file(&filepath) {
        Ok(d) => d,
        Err(e) => return (400, "application/json", json_err(&e)),
    };
    let heroes = match data {
        Value::Array(a) => a,
        _ => return (400, "application/json", json_err("存档格式错误: 应为数组")),
    };
    let hero_count = heroes.len();

    let mut save_data = None;
    if let Some(sp) = &save_path {
        if let Ok(d) = load_data_from_file(sp) {
            save_data = Some(d);
        }
    }

    with_state(|state| {
        state.hero_data = Some(heroes);
        state.hero_filepath = filepath.clone();
        if let (Some(sd), Some(sp)) = (save_data, save_path) {
            state.save_data = Some(sd);
            state.save_filepath = sp;
        }
        json_resp(
            200,
            &json!({"success": true, "hero_count": hero_count, "filepath": filepath}),
        )
    })
}

// ========== API: 英雄列表/详情 ==========

fn handle_heroes() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let mut heroes = Vec::new();
        for hero in arr {
            if hero.is_null() {
                continue;
            }
            let force_id = hero.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
            let nature = hero.get("nature").and_then(|v| v.as_i64()).unwrap_or(6);
            let talent_id = hero.get("talent").and_then(|v| v.as_i64()).unwrap_or(2);
            heroes.push(json!({
                "heroID": hero.get("heroID"),
                "heroName": field_or(hero, "heroName", json!("未知")),
                "age": field_or(hero, "age", json!(0)),
                "forceID": force_id,
                "forceName": force_name(force_id),
                "isLeader": field_or(hero, "isLeader", json!(false)),
                "dead": field_or(hero, "dead", json!(false)),
                "inTeam": field_or(hero, "inTeam", json!(false)),
                "isFemale": field_or(hero, "isFemale", json!(false)),
                "nature": nature,
                "natureName": nature_name(nature),
                "talent": talent_id,
                "talentName": get_talent_name(state, &json!(talent_id)),
                "hp": field_or(hero, "hp", json!(0)),
                "maxhp": field_or(hero, "maxhp", json!(0)),
                "fame": field_or(hero, "fame", json!(0)),
                "badFame": field_or(hero, "badFame", json!(0)),
            }));
        }
        json_resp(200, &json!(heroes))
    })
}

fn handle_hero_detail(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[idx];
        let force_id = hero.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
        let nature = hero.get("nature").and_then(|v| v.as_i64()).unwrap_or(6);
        let talent_id = hero.get("talent").and_then(|v| v.as_i64()).unwrap_or(2);
        let items_data = hero.get("itemListData").cloned().unwrap_or(json!({}));
        let result = json!({
            "heroID": hero.get("heroID"),
            "heroName": field_or(hero, "heroName", json!("未知")),
            "heroFamilyName": field_or(hero, "heroFamilyName", json!("")),
            "age": field_or(hero, "age", json!(0)),
            "isFemale": field_or(hero, "isFemale", json!(false)),
            "forceID": force_id,
            "forceName": force_name(force_id),
            "isLeader": field_or(hero, "isLeader", json!(false)),
            "forceJobID": field_or(hero, "forceJobID", json!(-1)),
            "heroForceLv": field_or(hero, "heroForceLv", json!(0)),
            "forceContribution": field_or(hero, "forceContribution", json!(0)),
            "nature": nature,
            "natureName": nature_name(nature),
            "talent": talent_id,
            "talentName": get_talent_name(state, &json!(talent_id)),
            "hp": field_or(hero, "hp", json!(0)),
            "maxhp": field_or(hero, "maxhp", json!(0)),
            "power": field_or(hero, "power", json!(0)),
            "maxPower": field_or(hero, "maxPower", json!(0)),
            "mana": field_or(hero, "mana", json!(0)),
            "maxMana": field_or(hero, "maxMana", json!(0)),
            "armor": field_or(hero, "armor", json!(0)),
            "internalInjury": field_or(hero, "internalInjury", json!(0)),
            "externalInjury": field_or(hero, "externalInjury", json!(0)),
            "poisonInjury": field_or(hero, "poisonInjury", json!(0)),
            "dead": field_or(hero, "dead", json!(false)),
            "inPrison": field_or(hero, "inPrison", json!(false)),
            "rest": field_or(hero, "rest", json!(false)),
            "inTeam": field_or(hero, "inTeam", json!(false)),
            "fame": field_or(hero, "fame", json!(0)),
            "badFame": field_or(hero, "badFame", json!(0)),
            "fightScore": field_or(hero, "fightScore", json!(0)),
            "baseAttri": field_or(hero, "baseAttri", json!([0,0,0,0,0,0])),
            "totalAttri": field_or(hero, "totalAttri", json!([0,0,0,0,0,0])),
            "maxAttri": field_or(hero, "maxAttri", json!([0,0,0,0,0,0])),
            "baseFightSkill": field_or(hero, "baseFightSkill", json!([0,0,0,0,0,0,0,0,0])),
            "totalFightSkill": field_or(hero, "totalFightSkill", json!([0,0,0,0,0,0,0,0,0])),
            "maxFightSkill": field_or(hero, "maxFightSkill", json!([0,0,0,0,0,0,0,0,0])),
            "baseLivingSkill": field_or(hero, "baseLivingSkill", json!([0,0,0,0,0,0,0,0,0])),
            "totalLivingSkill": field_or(hero, "totalLivingSkill", json!([0,0,0,0,0,0,0,0,0])),
            "maxLivingSkill": field_or(hero, "maxLivingSkill", json!([0,0,0,0,0,0,0,0,0])),
            "money": items_data.get("money").cloned().unwrap_or(json!(0)),
            "weight": items_data.get("weight").cloned().unwrap_or(json!(0)),
            "maxWeight": items_data.get("maxWeight").cloned().unwrap_or(json!(0)),
        });
        json_resp(200, &result)
    })
}

fn handle_hero_details(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[idx];
        let base_add = hero
            .get("baseAddData")
            .and_then(|x| x.get("heroSpeAddData"))
            .cloned()
            .unwrap_or(json!({}));
        let total_add = hero
            .get("totalAddData")
            .and_then(|x| x.get("heroSpeAddData"))
            .cloned()
            .unwrap_or(json!({}));
        json_resp(
            200,
            &json!({
                "realMaxHp": field_or(hero, "realMaxHp", json!(0)),
                "realMaxPower": field_or(hero, "realMaxPower", json!(0)),
                "realMaxMana": field_or(hero, "realMaxMana", json!(0)),
                "armor": field_or(hero, "armor", json!(0)),
                "fightScore": field_or(hero, "fightScore", json!(0)),
                "baseAddData": parse_spe_data_map(&base_add),
                "totalAddData": parse_spe_data_map(&total_add),
            }),
        )
    })
}

// ========== API: 英雄修改 (属性/基础/状态) ==========

fn handle_hero_attr(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let attr_type = body.get("type").and_then(|x| x.as_str()).unwrap_or("").to_string();
    let idx = match body.get("index").and_then(|x| x.as_i64()) {
        Some(i) if i >= 0 => i as usize,
        _ => return (400, "application/json", json_err("无效的索引")),
    };
    let value = v_f64(body.get("value").unwrap_or(&json!(0)));
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        let ok = match attr_type.as_str() {
            "base" => set_arr_f(hero, "baseAttri", idx, value) && set_arr_f(hero, "totalAttri", idx, value),
            "max" => set_arr_f(hero, "maxAttri", idx, value),
            "fight_base" => {
                set_arr_f(hero, "baseFightSkill", idx, value)
                    && set_arr_f(hero, "totalFightSkill", idx, value)
            }
            "fight_max" => set_arr_f(hero, "maxFightSkill", idx, value),
            "living_base" => {
                set_arr_f(hero, "baseLivingSkill", idx, value)
                    && set_arr_f(hero, "totalLivingSkill", idx, value)
            }
            "living_max" => set_arr_f(hero, "maxLivingSkill", idx, value),
            _ => return (400, "application/json", json_err("无效的属性类型")),
        };
        if !ok {
            return (400, "application/json", json_err("属性索引越界"));
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_basic(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let attr_type = body.get("type").and_then(|x| x.as_str()).unwrap_or("").to_string();
    let idx = match body.get("index").and_then(|x| x.as_i64()) {
        Some(i) if i >= 0 => i as usize,
        _ => return (400, "application/json", json_err("无效的索引")),
    };
    let value = v_f64(body.get("value").unwrap_or(&json!(0)));
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        let ok = match attr_type.as_str() {
            "base" => {
                set_arr_f(hero, "baseAttri", idx, value)
                    && set_arr_f(hero, "totalAttri", idx, value)
                    && set_arr_f(hero, "maxAttri", idx, value)
            }
            "fight" => {
                set_arr_f(hero, "baseFightSkill", idx, value)
                    && set_arr_f(hero, "totalFightSkill", idx, value)
                    && set_arr_f(hero, "maxFightSkill", idx, value)
            }
            "living" => {
                set_arr_f(hero, "baseLivingSkill", idx, value)
                    && set_arr_f(hero, "totalLivingSkill", idx, value)
                    && set_arr_f(hero, "maxLivingSkill", idx, value)
            }
            _ => return (400, "application/json", json_err("无效的属性类型")),
        };
        if !ok {
            return (400, "application/json", json_err("属性索引越界"));
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_fight_living(req: &Request, id: i64, kind: &str) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let idx = match body.get("index").and_then(|x| x.as_i64()) {
        Some(i) if i >= 0 => i as usize,
        _ => return (400, "application/json", json_err("无效的索引")),
    };
    let value = v_f64(body.get("value").unwrap_or(&json!(0)));
    let (base_key, total_key, max_key) = if kind == "fight" {
        ("baseFightSkill", "totalFightSkill", "maxFightSkill")
    } else {
        ("baseLivingSkill", "totalLivingSkill", "maxLivingSkill")
    };
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        let ok = set_arr_f(hero, base_key, idx, value)
            && set_arr_f(hero, total_key, idx, value)
            && set_arr_f(hero, max_key, idx, value);
        if !ok {
            return (400, "application/json", json_err("属性索引越界"));
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_status(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let hp = body.get("hp").map(v_f64);
    let power = body.get("power").map(v_f64);
    let mana = body.get("mana").map(v_f64);
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        modify_status(&mut arr[h_idx], hp, power, mana);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_fame(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let fame = body.get("fame").map(v_f64);
    let bad_fame = body.get("badFame").map(v_f64);
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        modify_fame(&mut arr[h_idx], fame, bad_fame);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_money(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let money = v_i64(body.get("money").unwrap_or(&json!(0))).clamp(0, 999999);
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        modify_money(&mut arr[h_idx], money);
        json_resp(200, &json!({"success": true, "money": money}))
    })
}

fn handle_detail_attr(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let attr_id = body
        .get("attrId")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .to_string();
    let value = v_f64(body.get("value").unwrap_or(&json!(0)));
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        if !hero.get("baseAddData").map(|v| v.is_object()).unwrap_or(false) {
            hero["baseAddData"] = json!({"heroSpeAddData": {}});
        }
        let hero_spe = hero
            .get_mut("baseAddData")
            .and_then(|v| v.as_object_mut());
        let hero_spe = match hero_spe {
            Some(m) => {
                if !m.get("heroSpeAddData").map(|v| v.is_object()).unwrap_or(false) {
                    m.insert("heroSpeAddData".to_string(), json!({}));
                }
                m.get_mut("heroSpeAddData").unwrap().as_object_mut().unwrap()
            }
            None => return (400, "application/json", json_err("数据错误")),
        };
        if value == 0.0 {
            hero_spe.remove(&attr_id);
        } else {
            hero_spe.insert(attr_id.clone(), json!(value));
        }
        json_resp(200, &json!({"success": true}))
    })
}

// ========== API: 门派信息 ==========

fn handle_hero_force(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[idx];
        let force_id = hero.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
        json_resp(
            200,
            &json!({
                "forceID": force_id,
                "forceName": force_name(force_id),
                "heroForceLv": field_or(hero, "heroForceLv", json!(0)),
                "forceContribution": field_or(hero, "forceContribution", json!(0)),
                "thisYearContribution": field_or(hero, "thisYearContribution", json!(0)),
                "lastYearContribution": field_or(hero, "lastYearContribution", json!(0)),
                "thisMonthContribution": field_or(hero, "thisMonthContribution", json!(0)),
                "lastMonthContribution": field_or(hero, "lastMonthContribution", json!(0)),
                "lastFightContribution": field_or(hero, "lastFightContribution", json!(0)),
                "governContribution": field_or(hero, "governContribution", json!(0)),
                "forceJobID": field_or(hero, "forceJobID", json!(-1)),
                "forceJobType": field_or(hero, "forceJobType", json!(-1)),
                "forceJobCD": field_or(hero, "forceJobCD", json!(0)),
            }),
        )
    })
}

fn handle_hero_force_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        for field in [
            "heroForceLv", "forceContribution", "thisYearContribution", "lastYearContribution",
            "thisMonthContribution", "lastMonthContribution", "lastFightContribution",
            "governContribution", "forceJobID", "forceJobType", "forceJobCD",
        ] {
            if let Some(v) = body.get(field) {
                if field.contains("Contribution") || field == "forceJobCD" {
                    hero[field] = json!(v_f64(v));
                } else {
                    hero[field] = json!(v_i64(v));
                }
            }
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_force_contributions(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let has_hero = state.hero_data.is_some();
        let has_save = state.save_data.is_some();
        if !has_hero || !has_save {
            return (400, "application/json", json_err("存档未加载"));
        }
        if id != 0 {
            return json_resp(
                200,
                &json!({"error": "只有主角有各派功绩数据", "contributions": []}),
            );
        }
        let forces = state
            .save_data
            .as_ref()
            .and_then(|s| s.get("Forces"))
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default();
        let mut contributions = Vec::new();
        for f in &forces {
            contributions.push(json!({
                "forceID": f.get("forceID"),
                "forceName": field_or(f, "forceName", json!("未知")),
                "contribution": field_or(f, "playerOutForceContribution", json!(0)),
            }));
        }
        json_resp(200, &json!({"contributions": contributions}))
    })
}

fn handle_force_contributions_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        if state.hero_data.is_none() || state.save_data.is_none() {
            return (400, "application/json", json_err("存档未加载"));
        }
        if id != 0 {
            return (400, "application/json", json_err("只有主角有各派功绩数据"));
        }
        let force_id = body.get("forceID").and_then(|x| x.as_i64());
        let contribution = v_f64(body.get("contribution").unwrap_or(&json!(0)));
        let save = state.save_data.as_mut().unwrap();
        if let Some(forces) = save.get_mut("Forces").and_then(|v| v.as_array_mut()) {
            for f in forces.iter_mut() {
                if f.get("forceID").and_then(|v| v.as_i64()) == force_id {
                    f["playerOutForceContribution"] = json!(contribution);
                    return json_resp(200, &json!({"success": true}));
                }
            }
        }
        (404, "application/json", json_err("门派未找到"))
    })
}

// ========== API: 天赋 ==========

fn handle_hero_talents(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[idx];
        let tags = hero.get("heroTagData").cloned().unwrap_or(json!([]));
        let mut tags_with_names = Vec::new();
        if let Some(list) = tags.as_array() {
            for tag in list {
                let tag_id = tag.get("tagID").cloned().unwrap_or(Value::Null);
                let tag_info = tag_id
                    .as_i64()
                    .and_then(|t| state.tag_names.get(&t))
                    .cloned()
                    .unwrap_or(json!({}));
                tags_with_names.push(json!({
                    "tagID": tag.get("tagID"),
                    "leftTime": tag.get("leftTime"),
                    "sourceHero": tag.get("sourceHero"),
                    "name": get_tag_name(state, &tag_id),
                    "description": tag_info.get("description").cloned().unwrap_or(json!("")),
                }));
            }
        }
        json_resp(
            200,
            &json!({
                "heroTagPoint": field_or(hero, "heroTagPoint", json!(0)),
                "heroTagData": tags_with_names,
            }),
        )
    })
}

fn handle_hero_talents_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        if let Some(v) = body.get("heroTagPoint") {
            hero["heroTagPoint"] = json!(v_f64(v));
        }
        if let Some(v) = body.get("heroTagData") {
            hero["heroTagData"] = v.clone();
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_talent_add(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let tag_id = match body.get("tagID").and_then(|x| x.as_i64()) {
        Some(t) => t,
        None => return (400, "application/json", json_err("缺少tagID")),
    };
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        let tags = hero.get("heroTagData").cloned().unwrap_or(json!([]));
        if let Some(list) = tags.as_array() {
            if list.iter().any(|t| t.get("tagID").and_then(|v| v.as_i64()) == Some(tag_id)) {
                return (400, "application/json", json_err("该天赋已存在"));
            }
        }
        let mut new_tags = if let Some(list) = tags.as_array() {
            list.clone()
        } else {
            Vec::new()
        };
        new_tags.push(json!({"tagID": tag_id, "leftTime": -1.0, "sourceHero": Value::Null}));
        hero["heroTagData"] = json!(new_tags);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_talent_delete(id: i64, tag_id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        if let Some(tags) = hero.get_mut("heroTagData").and_then(|v| v.as_array_mut()) {
            tags.retain(|t| t.get("tagID").and_then(|v| v.as_i64()) != Some(tag_id));
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_talent_put(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let talent = v_i64(body.get("talent").unwrap_or(&json!(2)));
    if !(0..=4).contains(&talent) {
        return (400, "application/json", json_err("天赋值必须在0-4之间"));
    }
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        arr[h_idx]["talent"] = json!(talent);
        let name = get_talent_name(state, &json!(talent));
        json_resp(200, &json!({"success": true, "talent": talent, "name": name}))
    })
}

// ========== API: 好感度 ==========

fn handle_hero_favor(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[idx];
        let favor = v_f64(hero.get("favor").unwrap_or(&json!(-999999.0)));
        let (status, status_text) = favor_status(favor);
        json_resp(
            200,
            &json!({
                "heroID": id,
                "heroName": field_or(hero, "heroName", json!("未知")),
                "favor": favor,
                "status": status,
                "statusText": status_text,
            }),
        )
    })
}

fn handle_hero_favor_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let value = v_f64(body.get("favor").unwrap_or(&json!(0)));
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        modify_favor(&mut arr[h_idx], value);
        let favor = arr[h_idx].get("favor").cloned().unwrap_or(json!(0));
        json_resp(200, &json!({"success": true, "favor": favor}))
    })
}

fn handle_heroes_favor() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let mut result = Vec::new();
        for hero in arr {
            if hero.is_null() {
                continue;
            }
            let favor = v_f64(hero.get("favor").unwrap_or(&json!(-999999.0)));
            let force_id = hero.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
            result.push(json!({
                "heroID": hero.get("heroID"),
                "heroName": field_or(hero, "heroName", json!("未知")),
                "favor": favor,
                "isUnknown": favor == -999999.0,
                "forceID": force_id,
                "forceName": force_name(force_id),
            }));
        }
        json_resp(200, &json!(result))
    })
}

fn handle_heroes_favor_batch(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let value = v_f64(body.get("favor").unwrap_or(&json!(0)));
    let mode = body.get("mode").and_then(|x| x.as_str()).unwrap_or("all").to_string();
    let target_force = body.get("forceID").and_then(|x| x.as_i64());
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let mut count = 0usize;
        for hero in arr.iter_mut() {
            if hero.is_null() {
                continue;
            }
            let matched = match mode.as_str() {
                "all" => true,
                "team" => hero.get("inTeam").and_then(|v| v.as_bool()).unwrap_or(false),
                "force" => hero.get("belongForceID").and_then(|v| v.as_i64()) == target_force,
                _ => false,
            };
            if matched {
                modify_favor(hero, value);
                count += 1;
            }
        }
        json_resp(200, &json!({"success": true, "count": count}))
    })
}

// ========== API: 技能 ==========

fn handle_hero_skills(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[idx];
        let skills = hero.get("kungfuSkills").cloned().unwrap_or(json!([]));
        let mut result = Vec::new();
        if let Some(skills) = skills.as_array() {
            for (i, skill) in skills.iter().enumerate() {
                let skill_id = skill.get("skillID").cloned().unwrap_or(Value::Null);
                let skill_info = skill_id
                    .as_i64()
                    .and_then(|sid| state.skill_names.get(&sid))
                    .cloned()
                    .unwrap_or(json!({}));
                let spe_data = skill
                    .get("speUseData")
                    .and_then(|x| x.get("heroSpeAddData"))
                    .cloned()
                    .unwrap_or(json!({}));
                let mut spe_parts = Vec::new();
                if let Some(map) = spe_data.as_object() {
                    for (k, v) in map.iter().take(3) {
                        spe_parts.push(format!("{}:{}", get_spe_attr_name(state, k), v));
                    }
                }
                let extra_data = skill
                    .get("extraAddData")
                    .and_then(|x| x.get("heroSpeAddData"))
                    .cloned()
                    .unwrap_or(json!({}));
                let extra_attrs = parse_spe_data_array(state, &extra_data);
                result.push(json!({
                    "index": i,
                    "skillID": skill_id,
                    "name": get_skill_name(state, skill.get("skillID").unwrap_or(&Value::Null)),
                    "type": skill_info.get("type").cloned().unwrap_or(json!("")),
                    "lv": field_or(skill, "lv", json!(0)),
                    "equiped": field_or(skill, "equiped", json!(false)),
                    "isNew": field_or(skill, "isNew", json!(false)),
                    "fightExp": field_or(skill, "fightExp", json!(0)),
                    "bookExp": field_or(skill, "bookExp", json!(0)),
                    "damageUseSpeAddValue": field_or(skill, "damageUseSpeAddValue", json!(0)),
                    "selfUseSpeAddValue": field_or(skill, "selfUseSpeAddValue", json!(0)),
                    "enemyUseSpeAddValue": field_or(skill, "enemyUseSpeAddValue", json!(0)),
                    "speAttrs": spe_parts.join(", "),
                    "extraAddData": extra_attrs,
                }));
            }
        }
        json_resp(200, &json!(result))
    })
}

fn handle_skill_detail(id: i64, idx: usize) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[h_idx];
        let skills = hero.get("kungfuSkills").cloned().unwrap_or(json!([]));
        let skills = match skills.as_array() {
            Some(s) => s,
            None => return (400, "application/json", json_err("武功序号无效")),
        };
        if idx >= skills.len() {
            return (400, "application/json", json_err("武功序号无效"));
        }
        let skill = &skills[idx];
        let skill_id = skill.get("skillID").cloned().unwrap_or(Value::Null);
        let skill_info = skill_id
            .as_i64()
            .and_then(|sid| state.skill_names.get(&sid))
            .cloned()
            .unwrap_or(json!({}));
        let spe_equip = skill
            .get("speEquipData")
            .and_then(|x| x.get("heroSpeAddData"))
            .cloned()
            .unwrap_or(json!({}));
        let spe_use = skill
            .get("speUseData")
            .and_then(|x| x.get("heroSpeAddData"))
            .cloned()
            .unwrap_or(json!({}));
        let extra = skill
            .get("extraAddData")
            .and_then(|x| x.get("heroSpeAddData"))
            .cloned()
            .unwrap_or(json!({}));
        let result = json!({
            "index": idx,
            "skillID": skill_id,
            "name": get_skill_name(state, skill.get("skillID").unwrap_or(&Value::Null)),
            "type": skill_info.get("type").cloned().unwrap_or(json!("")),
            "lv": field_or(skill, "lv", json!(0)),
            "equiped": field_or(skill, "equiped", json!(false)),
            "isNew": field_or(skill, "isNew", json!(false)),
            "fightExp": field_or(skill, "fightExp", json!(0)),
            "bookExp": field_or(skill, "bookExp", json!(0)),
            "damageUseSpeAddValue": field_or(skill, "damageUseSpeAddValue", json!(0)),
            "selfUseSpeAddValue": field_or(skill, "selfUseSpeAddValue", json!(0)),
            "enemyUseSpeAddValue": field_or(skill, "enemyUseSpeAddValue", json!(0)),
            "speEquipData": parse_spe_data_array(state, &spe_equip),
            "speUseData": parse_spe_data_array(state, &spe_use),
            "extraAddData": parse_spe_data_array(state, &extra),
        });
        json_resp(200, &result)
    })
}

fn handle_skill_update(req: &Request, id: i64, idx: usize) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let skills = arr[h_idx].get_mut("kungfuSkills").and_then(|v| v.as_array_mut());
        let skill = match skills {
            Some(s) if idx < s.len() => &mut s[idx],
            _ => return (400, "application/json", json_err("武功序号无效")),
        };
        if let Some(v) = body.get("lv") {
            skill["lv"] = json!(v_i64(v));
        }
        if let Some(v) = body.get("damageUseSpeAddValue") {
            skill["damageUseSpeAddValue"] = json!(v_f64(v));
        }
        if let Some(v) = body.get("selfUseSpeAddValue") {
            skill["selfUseSpeAddValue"] = json!(v_f64(v));
        }
        if let Some(v) = body.get("enemyUseSpeAddValue") {
            skill["enemyUseSpeAddValue"] = json!(v_f64(v));
        }
        if let Some(v) = body.get("equiped") {
            skill["equiped"] = json!(v.as_bool().unwrap_or(false));
        }
        for field in ["speEquipData", "speUseData", "extraAddData"] {
            if let Some(items) = body.get(field).and_then(|v| v.as_array()) {
                if !skill.get(field).map(|v| v.is_object()).unwrap_or(false) {
                    skill[field] = json!({"heroSpeAddData": {}});
                }
                let hero_spe = skill[field]
                    .as_object_mut()
                    .and_then(|m| m.get_mut("heroSpeAddData"));
                let hero_spe = match hero_spe {
                    Some(v) if v.is_object() => v.as_object_mut().unwrap(),
                    _ => {
                        if let Some(m) = skill.get_mut(field).and_then(|v| v.as_object_mut()) {
                            m.insert("heroSpeAddData".to_string(), json!({}));
                            m.get_mut("heroSpeAddData").unwrap().as_object_mut().unwrap()
                        } else {
                            continue;
                        }
                    }
                };
                hero_spe.clear();
                for item in items {
                    let attr_id = item.get("id").and_then(|x| x.as_str()).unwrap_or("").to_string();
                    let value = v_f64(item.get("value").unwrap_or(&json!(0)));
                    if value != 0.0 {
                        hero_spe.insert(attr_id, json!(value));
                    }
                }
            }
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_skill_delete(id: i64, idx: usize) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let removed = match remove_skill(&mut arr[h_idx], idx) {
            Some(r) => r,
            None => return (400, "application/json", json_err("武功序号无效")),
        };
        let name = get_skill_name(state, removed.get("skillID").unwrap_or(&Value::Null));
        json_resp(200, &json!({"success": true, "removed": name}))
    })
}

fn handle_skill_add(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let skill_id = body.get("skillID").cloned().unwrap_or(Value::Null);
    let lv = body.get("lv").cloned().unwrap_or(json!(1));
    with_state(|state| {
        let name = get_skill_name(state, &skill_id);
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        add_skill(&mut arr[h_idx], skill_id, lv);
        json_resp(200, &json!({"success": true, "name": name}))
    })
}

fn handle_action(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let action = body
        .get("action")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .to_string();
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        match action.as_str() {
            "max_all" => {
                let value = v_f64(body.get("value").unwrap_or(&json!(999)));
                max_all_attrs(hero, value);
            }
            "heal" => heal_hero(hero),
            "revive" => revive_hero(hero),
            "skills_max" => {
                let lv = v_i64(body.get("lv").unwrap_or(&json!(10)));
                let damage = v_f64(body.get("damage").unwrap_or(&json!(999)));
                all_skills_max(hero, lv, damage);
            }
            "money_max" => modify_money(hero, 999999),
            "fame_max" => modify_fame(hero, Some(99999.0), Some(0.0)),
            _ => return (400, "application/json", json_err("未知操作")),
        }
        json_resp(200, &json!({"success": true, "action": action}))
    })
}

fn handle_batch_action(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let action = body
        .get("action")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .to_string();
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let mut count = 0usize;
        for hero in arr.iter_mut() {
            match action.as_str() {
                "max_all" => {
                    let value = v_f64(body.get("value").unwrap_or(&json!(999)));
                    max_all_attrs(hero, value);
                }
                "heal" => heal_hero(hero),
                "revive" => {
                    if hero.get("dead").and_then(|v| v.as_bool()).unwrap_or(false) {
                        revive_hero(hero);
                    }
                }
                "skills_max" => {
                    let lv = v_i64(body.get("lv").unwrap_or(&json!(10)));
                    let damage = v_f64(body.get("damage").unwrap_or(&json!(999)));
                    all_skills_max(hero, lv, damage);
                }
                _ => {}
            }
            count += 1;
        }
        json_resp(200, &json!({"success": true, "action": action, "count": count}))
    })
}

// ========== API: 关系 ==========

fn resolve_ids(arr: &[Value], ids: &Value) -> Vec<Value> {
    let mut result = Vec::new();
    if let Some(list) = ids.as_array() {
        for rid in list {
            let mut name = format!("ID:{}", rid);
            if let Some(r) = rid.as_i64() {
                if let Some(h) = arr
                    .iter()
                    .find(|h| h.get("heroID").and_then(|v| v.as_i64()) == Some(r))
                {
                    name = get_str(h, "heroName", &name).to_string();
                }
            }
            result.push(json!({"id": rid, "name": name}));
        }
    }
    result
}

fn handle_hero_relations(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[h_idx];
        let friends = resolve_ids(arr, hero.get("Friends").unwrap_or(&Value::Null));
        let haters = resolve_ids(arr, hero.get("Haters").unwrap_or(&Value::Null));
        let students = resolve_ids(arr, hero.get("Students").unwrap_or(&Value::Null));
        let teacher_id = hero.get("Teacher").and_then(|v| v.as_i64()).unwrap_or(-1);
        let mut teacher = Value::Null;
        if teacher_id >= 0 {
            if let Some(h) = arr
                .iter()
                .find(|h| h.get("heroID").and_then(|v| v.as_i64()) == Some(teacher_id))
            {
                teacher = json!({"id": teacher_id, "name": get_str(h, "heroName", &format!("ID:{}", teacher_id))});
            }
        }
        let lover_id = hero.get("Lover").and_then(|v| v.as_i64()).unwrap_or(-1);
        let mut lover = Value::Null;
        if lover_id >= 0 {
            if let Some(h) = arr
                .iter()
                .find(|h| h.get("heroID").and_then(|v| v.as_i64()) == Some(lover_id))
            {
                lover = json!({"id": lover_id, "name": get_str(h, "heroName", &format!("ID:{}", lover_id))});
            }
        }
        json_resp(
            200,
            &json!({"friends": friends, "haters": haters, "students": students, "teacher": teacher, "lover": lover}),
        )
    })
}

fn handle_hero_relations_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let action = body.get("action").and_then(|x| x.as_str()).unwrap_or("").to_string();
    let target_id = body.get("targetID").and_then(|x| x.as_i64());
    let relation_type = body.get("type").and_then(|x| x.as_str()).unwrap_or("").to_string();
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        let target_id = match target_id {
            Some(t) => t,
            None => return (400, "application/json", json_err("缺少targetID")),
        };
        match action.as_str() {
            "add" => match relation_type.as_str() {
                "friend" => list_add(hero, "Friends", target_id),
                "hater" => list_add(hero, "Haters", target_id),
                "lover" => hero["Lover"] = json!(target_id),
                _ => return (400, "application/json", json_err("无效的关系类型")),
            },
            "remove" => match relation_type.as_str() {
                "friend" => list_remove(hero, "Friends", target_id),
                "hater" => list_remove(hero, "Haters", target_id),
                "lover" => hero["Lover"] = json!(-1),
                _ => return (400, "application/json", json_err("无效的关系类型")),
            },
            _ => return (400, "application/json", json_err("无效的操作")),
        }
        json_resp(200, &json!({"success": true}))
    })
}

// ========== API: 物品 ==========

fn get_item_detail(state: &State, item: &Value, index: usize) -> Value {
    let equip_data = item.get("equipmentData").cloned().unwrap_or(Value::Null);
    let has_equip = equip_data.is_object();
    let base_add = if has_equip {
        equip_data
            .get("baseAddData")
            .and_then(|x| x.get("heroSpeAddData"))
            .cloned()
            .unwrap_or(json!({}))
    } else {
        json!({})
    };
    let extra_add = if has_equip {
        equip_data
            .get("extraAddData")
            .and_then(|x| x.get("heroSpeAddData"))
            .cloned()
            .unwrap_or(json!({}))
    } else {
        json!({})
    };
    let t = item.get("type").and_then(|v| v.as_i64()).unwrap_or(0);
    json!({
        "index": index,
        "name": field_or(item, "name", json!("未知")),
        "itemID": field_or(item, "itemID", json!(0)),
        "type": t,
        "typeName": item_type_name(t),
        "itemLv": field_or(item, "itemLv", json!(0)),
        "rareLv": field_or(item, "rareLv", json!(0)),
        "weight": field_or(item, "weight", json!(0)),
        "value": field_or(item, "value", json!(0)),
        "equipped": if has_equip { v_bool(equip_data.get("equiped").unwrap_or(&json!(false))) } else { false },
        "baseAddData": parse_spe_data_array(state, &base_add),
        "extraAddData": parse_spe_data_array(state, &extra_add),
    })
}

fn handle_hero_items(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[h_idx];
        let items_data = hero.get("itemListData").cloned().unwrap_or(json!({}));
        let equip = hero.get("nowEquipment").cloned().unwrap_or(json!({}));
        let all_items = items_data.get("allItem").cloned().unwrap_or(json!([]));

        let mut equipped_items: BTreeMap<String, Value> = BTreeMap::new();
        if let (Some(equip_map), Some(items)) = (equip.as_object(), all_items.as_array()) {
            for (slot, records) in equip_map {
                if let Some(slot_name) = slot.strip_suffix("SaveRecord") {
                    if let Some(records) = records.as_array() {
                        for idx_v in records {
                            if let Some(idx) = idx_v.as_i64() {
                                if (0..items.len() as i64).contains(&idx) {
                                    let item = &items[idx as usize];
                                    if let Some(t) = item.get("type").and_then(|v| v.as_i64()) {
                                        if (0..=4).contains(&t) {
                                            let detail = get_item_detail(state, item, idx as usize);
                                            if slot_name == "decoration" {
                                                equipped_items
                                                    .entry("decorations".to_string())
                                                    .or_insert_with(|| json!([]))
                                                    .as_array_mut()
                                                    .unwrap()
                                                    .push(detail);
                                            } else {
                                                equipped_items.insert(slot_name.to_string(), detail);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        let mut items_by_type: BTreeMap<String, Vec<Value>> = BTreeMap::new();
        if let Some(items) = all_items.as_array() {
            for (i, item) in items.iter().enumerate() {
                let t = item.get("type").and_then(|v| v.as_i64()).unwrap_or(0);
                let type_name = item_type_name(t);
                let equip_data = item.get("equipmentData").cloned().unwrap_or(Value::Null);
                let equipped = if equip_data.is_object() {
                    v_bool(equip_data.get("equiped").unwrap_or(&json!(false)))
                } else {
                    false
                };
                items_by_type.entry(type_name.clone()).or_default().push(json!({
                    "index": i,
                    "name": field_or(item, "name", json!("未知")),
                    "itemLv": field_or(item, "itemLv", json!(0)),
                    "rareLv": field_or(item, "rareLv", json!(0)),
                    "type": t,
                    "equipped": equipped,
                }));
            }
        }
        let result = json!({
            "money": items_data.get("money").cloned().unwrap_or(json!(0)),
            "weight": items_data.get("weight").cloned().unwrap_or(json!(0)),
            "maxWeight": items_data.get("maxWeight").cloned().unwrap_or(json!(0)),
            "totalItems": all_items.as_array().map(|a| a.len()).unwrap_or(0),
            "equippedItems": equipped_items,
            "itemsByType": items_by_type,
        });
        json_resp(200, &result)
    })
}

fn handle_hero_item_detail(id: i64, item_idx: usize) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &arr[h_idx];
        let items = hero
            .get("itemListData")
            .and_then(|x| x.get("allItem"))
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default();
        if item_idx >= items.len() {
            return (400, "application/json", json_err("物品索引无效"));
        }
        json_resp(200, &get_item_detail(state, &items[item_idx], item_idx))
    })
}

fn handle_hero_item_update(req: &Request, id: i64, item_idx: usize) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        let items = hero
            .get_mut("itemListData")
            .and_then(|x| x.get_mut("allItem"))
            .and_then(|v| v.as_array_mut());
        let item = match items {
            Some(items) if item_idx < items.len() => &mut items[item_idx],
            _ => return (400, "application/json", json_err("物品索引无效")),
        };
        if let Some(field) = body.get("field").and_then(|x| x.as_str()) {
            let value = body.get("value").unwrap_or(&Value::Null);
            if field == "itemLv" || field == "rareLv" {
                item[field] = json!(v_i64(value));
            }
        }
        if let (Some(field_name), Some(attr_id)) = (
            body.get("fieldName").and_then(|x| x.as_str()),
            body.get("attrId").and_then(|x| x.as_str()),
        ) {
            let value = v_f64(body.get("value").unwrap_or(&json!(0)));
            if !item.get("equipmentData").map(|v| v.is_object()).unwrap_or(false) {
                item["equipmentData"] = json!({
                    "enhanceLv": 0, "littleType": 0, "attriType": 0,
                    "baseAddData": {"heroSpeAddData": {}},
                    "extraAddData": {"heroSpeAddData": {}},
                    "equiped": false,
                });
            }
            let equip_data = item.get_mut("equipmentData").and_then(|v| v.as_object_mut()).unwrap();
            if !equip_data.get(field_name).map(|v| v.is_object()).unwrap_or(false) {
                equip_data.insert(field_name.to_string(), json!({"heroSpeAddData": {}}));
            }
            let hero_spe = equip_data
                .get_mut(field_name)
                .and_then(|v| v.as_object_mut())
                .and_then(|m| m.get_mut("heroSpeAddData"))
                .and_then(|v| v.as_object_mut());
            if let Some(hero_spe) = hero_spe {
                if value == 0.0 {
                    hero_spe.remove(attr_id);
                } else {
                    hero_spe.insert(attr_id.to_string(), json!(value));
                }
            }
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_hero_item_delete(id: i64, item_idx: usize) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let removed = match remove_item(&mut arr[h_idx], item_idx) {
            Some(r) => r,
            None => return (400, "application/json", json_err("物品索引无效")),
        };
        let name = field_or(&removed, "name", json!("未知物品"))
            .as_str()
            .unwrap_or("未知物品")
            .to_string();
        json_resp(200, &json!({"success": true, "removed": name}))
    })
}

fn handle_hero_item_add(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let item = json!({
        "itemID": body.get("itemID").cloned().unwrap_or(json!(0)),
        "name": body.get("name").cloned().unwrap_or(json!("新物品")),
        "type": body.get("type").cloned().unwrap_or(json!(10)),
        "subType": body.get("subType").cloned().unwrap_or(json!(0)),
        "itemLv": body.get("itemLv").cloned().unwrap_or(json!(1)),
        "rareLv": body.get("rareLv").cloned().unwrap_or(json!(0)),
        "weight": body.get("weight").cloned().unwrap_or(json!(1.0)),
        "value": body.get("value").cloned().unwrap_or(json!(0)),
        "isNew": true,
        "poisonNum": 0.0,
        "poisonNumDetected": false,
        "equipmentData": Value::Null,
        "medFoodData": Value::Null,
        "bookData": Value::Null,
        "treasureData": Value::Null,
        "materialData": Value::Null,
        "horseData": Value::Null,
    });
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        add_item(&mut arr[h_idx], item.clone());
        json_resp(200, &json!({"success": true, "item": item}))
    })
}

fn handle_hero_items_batch(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let action = body.get("action").and_then(|x| x.as_str()).unwrap_or("").to_string();
    with_state(|state| {
        let arr = match &mut state.hero_data {
            Some(a) => a,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let h_idx = match find_hero_idx(arr, id) {
            Some(i) => i,
            None => return (404, "application/json", json_err("角色未找到")),
        };
        let hero = &mut arr[h_idx];
        match action.as_str() {
            "remove_all_type" => {
                let item_type = body.get("type").and_then(|x| x.as_i64());
                let mut removed = 0usize;
                if let Some(ild) = hero.get_mut("itemListData") {
                    if let Some(items) = ild.get_mut("allItem").and_then(|v| v.as_array_mut()) {
                        let before = items.len();
                        items.retain(|i| i.get("type").and_then(|v| v.as_i64()) != item_type);
                        removed = before - items.len();
                    }
                }
                json_resp(200, &json!({"success": true, "removed": removed}))
            }
            "remove_duplicates" => {
                let mut removed = 0usize;
                if let Some(ild) = hero.get_mut("itemListData") {
                    if let Some(items) = ild.get_mut("allItem").and_then(|v| v.as_array_mut()) {
                        let before = items.len();
                        let mut seen = std::collections::BTreeSet::new();
                        items.retain(|i| {
                            let name = i.get("name").and_then(|v| v.as_str()).unwrap_or("").to_string();
                            seen.insert(name.clone())
                        });
                        removed = before - items.len();
                    }
                }
                json_resp(200, &json!({"success": true, "removed": removed}))
            }
            _ => (400, "application/json", json_err("无效的操作")),
        }
    })
}

fn handle_items_types() -> (u16, &'static str, Vec<u8>) {
    let mut list = Vec::new();
    for (i, name) in ITEM_TYPES.iter().enumerate() {
        list.push(json!({"id": i, "name": name}));
    }
    json_resp(200, &json!(list))
}

// ========== API: 搜索 ==========

fn handle_skills_search(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let q = req
        .query
        .get("q")
        .map(|s| s.trim().to_lowercase())
        .unwrap_or_default();
    if q.is_empty() {
        return json_resp(200, &json!([]));
    }
    with_state(|state| {
        let mut matches = Vec::new();
        for (sid, info) in state.skill_names.iter() {
            let name = get_str(info, "name", "");
            if name.to_lowercase().contains(&q) {
                matches.push(json!({
                    "id": sid,
                    "name": name,
                    "type": info.get("type").cloned().unwrap_or(json!("")),
                }));
                if matches.len() >= 50 {
                    break;
                }
            }
        }
        json_resp(200, &json!(matches))
    })
}

fn handle_attrs_search(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let q = req
        .query
        .get("q")
        .map(|s| s.trim().to_lowercase())
        .unwrap_or_default();
    with_state(|state| {
        let mut matches = Vec::new();
        for (aid, aname) in state.spe_attr_map.iter() {
            if q.is_empty() || aname.to_lowercase().contains(&q) {
                matches.push(json!({"id": aid, "name": aname}));
            }
        }
        json_resp(200, &json!(matches))
    })
}

fn handle_tags_search(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let q = req
        .query
        .get("q")
        .map(|s| s.trim().to_lowercase())
        .unwrap_or_default();
    with_state(|state| {
        let mut matches = Vec::new();
        for (tid, info) in state.tag_names.iter() {
            let name = get_str(info, "name", "");
            let desc = get_str(info, "description", "");
            if q.is_empty() || name.to_lowercase().contains(&q) || desc.to_lowercase().contains(&q) {
                let desc_out: String = if desc.chars().count() > 50 {
                    format!("{}...", desc.chars().take(50).collect::<String>())
                } else {
                    desc.to_string()
                };
                matches.push(json!({
                    "id": tid,
                    "name": name,
                    "description": desc_out,
                    "category": info.get("category").cloned().unwrap_or(json!("")),
                }));
                if matches.len() >= 100 {
                    break;
                }
            }
        }
        json_resp(200, &json!(matches))
    })
}

// ========== API: 保存 / 备份 ==========

fn backup_file_copy(filepath: &str) -> Result<String, String> {
    let ts = local_timestamp();
    let backup_path = format!("{}.backup_{}", filepath, ts);
    std::fs::copy(filepath, &backup_path).map_err(|e| format!("备份失败: {}", e))?;
    Ok(backup_path)
}

fn handle_save() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let heroes = match &state.hero_data {
            Some(h) => h,
            None => return (400, "application/json", json_err("存档未加载")),
        };
        let backup_path = match backup_file_copy(&state.hero_filepath) {
            Ok(b) => b,
            Err(e) => return (400, "application/json", json_err(&e)),
        };
        let bytes = match serde_json::to_vec(heroes) {
            Ok(b) => b,
            Err(e) => return (400, "application/json", json_err(&format!("序列化失败: {}", e))),
        };
        if let Err(e) = std::fs::write(&state.hero_filepath, bytes) {
            return (400, "application/json", json_err(&format!("保存失败: {}", e)));
        }
        if let (Some(save_data), true) = (&state.save_data, !state.save_filepath.is_empty()) {
            let _ = backup_file_copy(&state.save_filepath);
            if let Ok(bytes) = serde_json::to_vec(save_data) {
                let _ = std::fs::write(&state.save_filepath, bytes);
            }
        }
        json_resp(200, &json!({"success": true, "backup": backup_path}))
    })
}

fn handle_backup() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        if state.hero_data.is_none() {
            return (400, "application/json", json_err("存档未加载"));
        }
        let backup_path = match backup_file_copy(&state.hero_filepath) {
            Ok(b) => b,
            Err(e) => return (400, "application/json", json_err(&e)),
        };
        json_resp(200, &json!({"success": true, "backup": backup_path}))
    })
}

fn handle_save_file_save() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save_data = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let backup_path = match backup_file_copy(&state.save_filepath) {
            Ok(b) => b,
            Err(e) => return (400, "application/json", json_err(&e)),
        };
        if let Ok(bytes) = serde_json::to_vec(save_data) {
            if let Err(e) = std::fs::write(&state.save_filepath, bytes) {
                return (400, "application/json", json_err(&format!("保存失败: {}", e)));
            }
        }
        json_resp(200, &json!({"success": true, "backup": backup_path}))
    })
}

// ========== API: Save 世界存档 ==========

fn handle_save_status() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(
            200,
            &json!({
                "loaded": true,
                "filepath": state.save_filepath,
                "chapter": field_or(save, "chapter", json!(1)),
                "worldTime": field_or(save, "worldTime", json!({})),
                "hour": field_or(save, "hour", json!(0)),
                "gameMode": field_or(save, "gameMode", json!(0)),
                "gameDifficulty": field_or(save, "gameDifficulty", json!(1)),
                "relaxMode": field_or(save, "relaxMode", json!(false)),
                "cheating": field_or(save, "cheating", json!(false)),
                "cheated": field_or(save, "cheated", json!(false)),
                "totalFightCount": field_or(save, "totalFightCount", json!(0)),
                "totalWinFightCount": field_or(save, "totalWinFightCount", json!(0)),
                "totalEnemyKilled": field_or(save, "totalEnemyKilled", json!(0)),
                "totalHeroMeet": field_or(save, "totalHeroMeet", json!(0)),
                "finishForceMissionCount": field_or(save, "finishForceMissionCount", json!(0)),
                "areasCount": save.get("Areas").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
                "forcesCount": save.get("Forces").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
                "resourcePointsCount": save.get("ResourcePoints").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
                "innsCount": save.get("Inns").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
            }),
        )
    })
}

fn handle_save_world_time_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(
            200,
            &save
                .get("worldTime")
                .cloned()
                .unwrap_or(json!({"year": 1, "month": 1, "day": 1})),
        )
    })
}

fn handle_save_world_time_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let mut wt = save
            .get("worldTime")
            .cloned()
            .unwrap_or(json!({"year": 1, "month": 1, "day": 1}));
        if let Some(y) = body.get("year") {
            wt["year"] = json!(v_i64(y).max(1));
        }
        if let Some(m) = body.get("month") {
            wt["month"] = json!(v_i64(m).clamp(1, 12));
        }
        if let Some(d) = body.get("day") {
            wt["day"] = json!(v_i64(d).clamp(1, 30));
        }
        save["worldTime"] = wt.clone();
        json_resp(200, &json!({"success": true, "worldTime": wt}))
    })
}

fn handle_save_game_settings_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(
            200,
            &json!({
                "chapter": field_or(save, "chapter", json!(1)),
                "gameMode": field_or(save, "gameMode", json!(0)),
                "gameDifficulty": field_or(save, "gameDifficulty", json!(1)),
                "relaxMode": field_or(save, "relaxMode", json!(false)),
                "cheating": field_or(save, "cheating", json!(false)),
                "cheated": field_or(save, "cheated", json!(false)),
                "hour": field_or(save, "hour", json!(0)),
                "TimeDifficulty": field_or(save, "TimeDifficulty", json!(10.0)),
                "battleTimeScale": field_or(save, "battleTimeScale", json!(10.0)),
            }),
        )
    })
}

fn handle_save_game_settings_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        apply_field(save, &body, "chapter", FT::I);
        apply_field(save, &body, "gameMode", FT::I);
        apply_field(save, &body, "gameDifficulty", FT::I);
        apply_field(save, &body, "relaxMode", FT::B);
        apply_field(save, &body, "cheating", FT::B);
        apply_field(save, &body, "hour", FT::F);
        apply_field(save, &body, "TimeDifficulty", FT::F);
        apply_field(save, &body, "battleTimeScale", FT::F);
        json_resp(200, &json!({"success": true}))
    })
}

const MONTH_LIMIT_FIELDS: [&str; 14] = [
    "monthCatchBadFamePlayerTime",
    "monthGambleTime",
    "monthPartyTime",
    "monthForcePartyTime",
    "monthDoctorTime",
    "monthPerformForMoneyTime",
    "monthCoachTime",
    "monthAttackMartialClubTime",
    "monthChallengeTime",
    "monthBuyAreaInfoTime",
    "monthGiveMoneyToGovernTime",
    "monthKillTime",
    "monthFreshBountyTime",
    "monthFreshAuctionTime",
];

const RESET_MONTH_FIELDS: [&str; 19] = [
    "monthCatchBadFamePlayerTime",
    "monthGambleTime",
    "monthPartyTime",
    "monthForcePartyTime",
    "monthDoctorTime",
    "monthPerformForMoneyTime",
    "monthCoachTime",
    "monthAttackMartialClubTime",
    "monthChallengeTime",
    "monthBuyAreaInfoTime",
    "monthGiveMoneyToGovernTime",
    "monthKillTime",
    "monthFreshBountyTime",
    "monthFreshAuctionTime",
    "monthSpeReduceBadFameTime",
    "monthSpeAddFameTime",
    "monthSpeGetTalentPointTime",
    "monthBreakEquipTime",
    "monthLeaderInteractOtherForceTime",
];

fn handle_save_month_limits_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let mut m = Map::new();
        for f in MONTH_LIMIT_FIELDS {
            m.insert(f.to_string(), field_or(save, f, json!(0)));
        }
        json_resp(200, &Value::Object(m))
    })
}

fn handle_save_month_limits_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        for f in MONTH_LIMIT_FIELDS {
            apply_field(save, &body, f, FT::I);
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_reset_month_limits() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        for f in RESET_MONTH_FIELDS {
            if save.get(f).is_some() {
                save[f] = json!(0);
            }
        }
        json_resp(200, &json!({"success": true}))
    })
}

const STAT_FIELDS: [&str; 9] = [
    "totalFightCount",
    "totalWinFightCount",
    "totalEnemyKilled",
    "totalBadFame",
    "totalHeroMeet",
    "finishForceMissionCount",
    "studyFightWithGreatHeroSingleWinNum",
    "studyFightWithGreatHeroMultiWinNum",
    "studyFightWithGreatHeroFinalWinNum",
];

fn handle_save_statistics_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let mut m = Map::new();
        for f in STAT_FIELDS {
            m.insert(f.to_string(), field_or(save, f, json!(0)));
        }
        json_resp(200, &Value::Object(m))
    })
}

fn handle_save_statistics_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        for f in STAT_FIELDS {
            if body.get(f).is_some() {
                if f == "totalBadFame" {
                    apply_field(save, &body, f, FT::F);
                } else {
                    apply_field(save, &body, f, FT::I);
                }
            }
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_areas() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let areas = save.get("Areas").cloned().unwrap_or(json!([]));
        let mut result = Vec::new();
        if let Some(list) = areas.as_array() {
            for area in list {
                let force_id = area.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
                result.push(json!({
                    "areaID": area.get("areaID"),
                    "areaName": field_or(area, "areaName", json!("未知")),
                    "areaType": field_or(area, "areaType", json!(0)),
                    "belongForceID": force_id,
                    "forceName": if force_id == -1 { "无".to_string() } else { force_name(force_id) },
                    "people": field_or(area, "people", json!(0)),
                    "maxPeople": field_or(area, "maxPeople", json!(0)),
                    "safe": field_or(area, "safe", json!(0)),
                    "support": field_or(area, "support", json!(0)),
                    "defence": field_or(area, "defence", json!(0)),
                    "insideHerosCount": area.get("insideHeros").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
                }));
            }
        }
        json_resp(200, &json!(result))
    })
}

fn area_buildings(_state: &State, area: &Value) -> Vec<Value> {
    let mut buildings = Vec::new();
    if let Some(tiles) = area.get("areaTiles").and_then(|v| v.as_array()) {
        for (i, tile) in tiles.iter().enumerate() {
            if let Some(b) = tile.get("building") {
                buildings.push(json!({
                    "tileIndex": i,
                    "row": tile.get("row"),
                    "column": tile.get("column"),
                    "buildingID": b.get("buildingID"),
                    "lv": field_or(b, "lv", json!(0)),
                    "buildTimeLeft": field_or(b, "buildTimeLeft", json!(0)),
                    "upgradeTimeLeft": field_or(b, "upgradeTimeLeft", json!(0)),
                    "produceRate": field_or(b, "produceRate", json!(0)),
                    "resourceStoreRate": field_or(b, "resourceStoreRate", json!(0)),
                }));
            }
        }
    }
    buildings
}

fn handle_save_area_detail(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let area = match find_area(save, id) {
            Some(a) => a,
            None => return (404, "application/json", json_err("区域未找到")),
        };
        let force_id = area.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
        let buildings = area_buildings(state, area);
        json_resp(
            200,
            &json!({
                "areaID": area.get("areaID"),
                "areaName": field_or(area, "areaName", json!("未知")),
                "areaType": field_or(area, "areaType", json!(0)),
                "areaStartLv": field_or(area, "areaStartLv", json!(1)),
                "belongForceID": force_id,
                "forceName": if force_id == -1 { "无".to_string() } else { force_name(force_id) },
                "bigMapPos": field_or(area, "bigMapPos", json!({})),
                "people": field_or(area, "people", json!(0)),
                "maxPeople": field_or(area, "maxPeople", json!(0)),
                "safe": field_or(area, "safe", json!(0)),
                "support": field_or(area, "support", json!(0)),
                "defence": field_or(area, "defence", json!(0)),
                "changeAreaState": field_or(area, "changeAreaState", json!([])),
                "changeResource": field_or(area, "changeResource", json!([])),
                "resourceValueRateBase": field_or(area, "resourceValueRateBase", json!([])),
                "insideHeros": field_or(area, "insideHeros", json!([])),
                "connectAreaID": field_or(area, "connectAreaID", json!([])),
                "connectResourcePointID": field_or(area, "connectResourcePointID", json!([])),
                "speProduct": field_or(area, "speProduct", json!([])),
                "branchLeaderID": field_or(area, "branchLeaderID", json!(-1)),
                "areaBranchDefenceLv": field_or(area, "areaBranchDefenceLv", json!([])),
                "missionNumCount": field_or(area, "missionNumCount", json!(0)),
                "plotNumCount": field_or(area, "plotNumCount", json!(0)),
                "thisMonthManaged": field_or(area, "thisMonthManaged", json!(0)),
                "buildings": buildings,
            }),
        )
    })
}

fn handle_save_area_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let areas = save.get_mut("Areas").and_then(|v| v.as_array_mut());
        let area = match areas {
            Some(list) => match list.iter_mut().find(|a| a.get("areaID").and_then(|v| v.as_i64()) == Some(id)) {
                Some(a) => a,
                None => return (404, "application/json", json_err("区域未找到")),
            },
            None => return (404, "application/json", json_err("区域未找到")),
        };
        apply_field(area, &body, "belongForceID", FT::I);
        apply_field(area, &body, "people", FT::F);
        apply_field(area, &body, "maxPeople", FT::F);
        apply_field(area, &body, "safe", FT::F);
        apply_field(area, &body, "support", FT::F);
        apply_field(area, &body, "defence", FT::F);
        apply_field(area, &body, "changeResource", FT::FL);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_area_buildings(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let area = match find_area(save, id) {
            Some(a) => a,
            None => return (404, "application/json", json_err("区域未找到")),
        };
        json_resp(200, &json!(area_buildings(state, area)))
    })
}

fn handle_save_area_building_update(req: &Request, id: i64, tile_index: usize) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let areas = save.get_mut("Areas").and_then(|v| v.as_array_mut());
        let area = match areas {
            Some(list) => match list.iter_mut().find(|a| a.get("areaID").and_then(|v| v.as_i64()) == Some(id)) {
                Some(a) => a,
                None => return (404, "application/json", json_err("区域未找到")),
            },
            None => return (404, "application/json", json_err("区域未找到")),
        };
        let tiles = area.get_mut("areaTiles").and_then(|v| v.as_array_mut());
        let tile = match tiles {
            Some(t) if tile_index < t.len() => &mut t[tile_index],
            _ => return (400, "application/json", json_err("地块索引无效")),
        };
        if !tile.get("building").map(|v| v.is_object()).unwrap_or(false) {
            return (400, "application/json", json_err("该地块没有建筑"));
        }
        let building = tile.get_mut("building").unwrap();
        apply_field(building, &body, "lv", FT::I);
        apply_field(building, &body, "buildTimeLeft", FT::I);
        apply_field(building, &body, "upgradeTimeLeft", FT::I);
        apply_field(building, &body, "produceRate", FT::F);
        apply_field(building, &body, "resourceStoreRate", FT::F);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_area_buildings_batch(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    let target_lv = match body.get("lv").and_then(|x| x.as_i64()) {
        Some(l) => l,
        None => return (400, "application/json", json_err("缺少等级参数")),
    };
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let areas = save.get_mut("Areas").and_then(|v| v.as_array_mut());
        let area = match areas {
            Some(list) => match list.iter_mut().find(|a| a.get("areaID").and_then(|v| v.as_i64()) == Some(id)) {
                Some(a) => a,
                None => return (404, "application/json", json_err("区域未找到")),
            },
            None => return (404, "application/json", json_err("区域未找到")),
        };
        let mut count = 0usize;
        if let Some(tiles) = area.get_mut("areaTiles").and_then(|v| v.as_array_mut()) {
            for tile in tiles.iter_mut() {
                if let Some(building) = tile.get_mut("building") {
                    building["lv"] = json!(target_lv);
                    building["buildTimeLeft"] = json!(0);
                    building["upgradeTimeLeft"] = json!(0);
                    count += 1;
                }
            }
        }
        json_resp(200, &json!({"success": true, "count": count}))
    })
}

fn handle_save_forces() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let forces = save.get("Forces").cloned().unwrap_or(json!([]));
        let mut result = Vec::new();
        if let Some(list) = forces.as_array() {
            for force in list {
                result.push(json!({
                    "forceID": force.get("forceID"),
                    "forceName": field_or(force, "forceName", json!("未知")),
                    "forceLv": field_or(force, "forceLv", json!(1)),
                    "bigForce": field_or(force, "bigForce", json!(false)),
                    "forceStyle": field_or(force, "forceStyle", json!("中庸")),
                    "leader": field_or(force, "leader", json!(-1)),
                    "mainAreaID": field_or(force, "mainAreaID", json!(-1)),
                    "ownAreasCount": force.get("ownAreasID").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
                    "ownHerosCount": force.get("ownHeros").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
                    "totalPopulation": field_or(force, "totalPopulation", json!(0)),
                    "totalSalary": field_or(force, "totalSalary", json!(0)),
                    "resourceStore": field_or(force, "resourceStore", json!([])),
                    "allyForce": field_or(force, "allyForce", json!([])),
                }));
            }
        }
        json_resp(200, &json!(result))
    })
}

fn handle_save_force_detail(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let force = match find_force(save, id) {
            Some(f) => f,
            None => return (404, "application/json", json_err("门派未找到")),
        };
        json_resp(
            200,
            &json!({
                "forceID": force.get("forceID"),
                "forceName": field_or(force, "forceName", json!("未知")),
                "forceLv": field_or(force, "forceLv", json!(1)),
                "bigForce": field_or(force, "bigForce", json!(false)),
                "forceStyle": field_or(force, "forceStyle", json!("中庸")),
                "leader": field_or(force, "leader", json!(-1)),
                "mainAreaID": field_or(force, "mainAreaID", json!(-1)),
                "masterForce": field_or(force, "masterForce", json!(-1)),
                "servantForce": field_or(force, "servantForce", json!([])),
                "ownAreasID": field_or(force, "ownAreasID", json!([])),
                "ownResourcePointsID": field_or(force, "ownResourcePointsID", json!([])),
                "ownHeros": field_or(force, "ownHeros", json!([])),
                "totalPopulation": field_or(force, "totalPopulation", json!(0)),
                "totalSalary": field_or(force, "totalSalary", json!(0)),
                "resourceStore": field_or(force, "resourceStore", json!([])),
                "resourceStoreMax": field_or(force, "resourceStoreMax", json!([])),
                "resourceChange": field_or(force, "resourceChange", json!([])),
                "forceStorage": field_or(force, "forceStorage", json!({})),
                "allyForce": field_or(force, "allyForce", json!([])),
                "kungfuSkillFocus": field_or(force, "kungfuSkillFocus", json!([])),
                "livingSkillFocus": field_or(force, "livingSkillFocus", json!([])),
                "nowResearchTech": field_or(force, "nowResearchTech", json!(-1)),
                "speBuildingID": field_or(force, "speBuildingID", json!(-1)),
            }),
        )
    })
}

fn handle_save_force_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let forces = save.get_mut("Forces").and_then(|v| v.as_array_mut());
        let force = match forces {
            Some(list) => match list.iter_mut().find(|f| f.get("forceID").and_then(|v| v.as_i64()) == Some(id)) {
                Some(f) => f,
                None => return (404, "application/json", json_err("门派未找到")),
            },
            None => return (404, "application/json", json_err("门派未找到")),
        };
        apply_field(force, &body, "forceLv", FT::I);
        apply_field(force, &body, "totalPopulation", FT::I);
        apply_field(force, &body, "totalSalary", FT::I);
        apply_field(force, &body, "resourceStore", FT::FL);
        apply_field(force, &body, "resourceStoreMax", FT::FL);
        apply_field(force, &body, "leader", FT::I);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_force_favor(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let force = match find_force(save, id) {
            Some(f) => f,
            None => return (404, "application/json", json_err("门派未找到")),
        };
        let favor_dict = force.get("forceFavorDict").cloned().unwrap_or(json!({}));
        let forces = save.get("Forces").cloned().unwrap_or(json!([]));
        let mut favors = Vec::new();
        if let Some(dict) = favor_dict.as_object() {
            for (other_id_str, favor) in dict {
                let other_id = other_id_str.parse::<i64>().unwrap_or(-1);
                let other_name = if let Some(list) = forces.as_array() {
                    list.iter()
                        .find(|f| f.get("forceID").and_then(|v| v.as_i64()) == Some(other_id))
                        .and_then(|f| f.get("forceName").and_then(|v| v.as_str()))
                        .map(String::from)
                        .unwrap_or_else(|| force_name(other_id))
                } else {
                    force_name(other_id)
                };
                favors.push(json!({
                    "forceID": other_id,
                    "forceName": other_name,
                    "favor": favor,
                }));
            }
        }
        json_resp(
            200,
            &json!({
                "forceID": id,
                "forceName": field_or(force, "forceName", json!("未知")),
                "favors": favors,
            }),
        )
    })
}

fn handle_save_force_favor_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let forces = save.get_mut("Forces").and_then(|v| v.as_array_mut());
        let force = match forces {
            Some(list) => match list.iter_mut().find(|f| f.get("forceID").and_then(|v| v.as_i64()) == Some(id)) {
                Some(f) => f,
                None => return (404, "application/json", json_err("门派未找到")),
            },
            None => return (404, "application/json", json_err("门派未找到")),
        };
        let target_id = body.get("forceID").and_then(|x| x.as_i64());
        let favor = v_f64(body.get("favor").unwrap_or(&json!(0)));
        if let Some(target_id) = target_id {
            let dict = force
                .get_mut("forceFavorDict")
                .and_then(|v| v.as_object_mut());
            if let Some(dict) = dict {
                dict.insert(target_id.to_string(), json!(favor));
            } else {
                let mut new_dict = Map::new();
                new_dict.insert(target_id.to_string(), json!(favor));
                force["forceFavorDict"] = Value::Object(new_dict);
            }
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_resource_points() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let rps = save.get("ResourcePoints").cloned().unwrap_or(json!([]));
        let mut result = Vec::new();
        if let Some(list) = rps.as_array() {
            for rp in list {
                let force_id = rp.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
                result.push(json!({
                    "resourcePointID": rp.get("resourcePointID"),
                    "resourcePointName": field_or(rp, "resourcePointName", json!("未知")),
                    "resourcePointTypeID": field_or(rp, "resourcePointTypeID", json!(0)),
                    "belongForceID": force_id,
                    "forceName": if force_id == -1 { "无".to_string() } else { force_name(force_id) },
                    "connectAreaID": field_or(rp, "connectAreaID", json!(-1)),
                    "changeResource": field_or(rp, "changeResource", json!([])),
                }));
            }
        }
        json_resp(200, &json!(result))
    })
}

fn find_resource_point<'a>(save: &'a Value, id: i64) -> Option<&'a Value> {
    save.get("ResourcePoints")?
        .as_array()?
        .iter()
        .find(|r| r.get("resourcePointID").and_then(|v| v.as_i64()) == Some(id))
}

fn handle_save_resource_point_detail(id: i64) -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let rp = match find_resource_point(save, id) {
            Some(r) => r,
            None => return (404, "application/json", json_err("资源点未找到")),
        };
        let force_id = rp.get("belongForceID").and_then(|v| v.as_i64()).unwrap_or(-1);
        json_resp(
            200,
            &json!({
                "resourcePointID": rp.get("resourcePointID"),
                "resourcePointName": field_or(rp, "resourcePointName", json!("未知")),
                "resourcePointFullName": field_or(rp, "resourcePointFullName", json!("")),
                "resourcePointTypeID": field_or(rp, "resourcePointTypeID", json!(0)),
                "belongForceID": force_id,
                "forceName": if force_id == -1 { "无".to_string() } else { force_name(force_id) },
                "connectAreaID": field_or(rp, "connectAreaID", json!(-1)),
                "changeResource": field_or(rp, "changeResource", json!([])),
            }),
        )
    })
}

fn handle_save_resource_point_update(req: &Request, id: i64) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let rps = save.get_mut("ResourcePoints").and_then(|v| v.as_array_mut());
        let rp = match rps {
            Some(list) => match list.iter_mut().find(|r| r.get("resourcePointID").and_then(|v| v.as_i64()) == Some(id)) {
                Some(r) => r,
                None => return (404, "application/json", json_err("资源点未找到")),
            },
            None => return (404, "application/json", json_err("资源点未找到")),
        };
        apply_field(rp, &body, "belongForceID", FT::I);
        apply_field(rp, &body, "changeResource", FT::FL);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_prison_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(200, &save.get("prisonData").cloned().unwrap_or(json!({})))
    })
}

fn handle_save_prison_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let mut prison = save.get("prisonData").cloned().unwrap_or(json!({}));
        apply_field(&mut prison, &body, "guardAlert", FT::F);
        apply_field(&mut prison, &body, "guardFavor", FT::F);
        apply_field(&mut prison, &body, "buyGuardCd", FT::F);
        save["prisonData"] = prison;
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_govern_storage_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let gs = save.get("governStorage").cloned().unwrap_or(json!({}));
        json_resp(
            200,
            &json!({
                "heroID": gs.get("heroID").cloned().unwrap_or(json!(-1)),
                "forceID": gs.get("forceID").cloned().unwrap_or(json!(-1)),
                "money": gs.get("money").cloned().unwrap_or(json!(0)),
                "weight": gs.get("weight").cloned().unwrap_or(json!(0)),
                "maxWeight": gs.get("maxWeight").cloned().unwrap_or(json!(-1)),
                "itemCount": gs.get("allItem").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
            }),
        )
    })
}

fn handle_save_govern_storage_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        let mut gs = save.get("governStorage").cloned().unwrap_or(json!({}));
        apply_field(&mut gs, &body, "money", FT::I);
        save["governStorage"] = gs;
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_unlock_flags_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(
            200,
            &json!({
                "openLeaveForce": field_or(save, "openLeaveForce", json!(false)),
                "openForceBuilding": field_or(save, "openForceBuilding", json!(false)),
                "openForceAttackResource": field_or(save, "openForceAttackResource", json!(false)),
                "openForceAttackArea": field_or(save, "openForceAttackArea", json!(false)),
                "openForceAttackBasement": field_or(save, "openForceAttackBasement", json!(false)),
            }),
        )
    })
}

fn handle_save_unlock_flags_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        for field in [
            "openLeaveForce",
            "openForceBuilding",
            "openForceAttackResource",
            "openForceAttackArea",
            "openForceAttackBasement",
        ] {
            apply_field(save, &body, field, FT::B);
        }
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_unlock_all() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        save["openLeaveForce"] = json!(true);
        save["openForceBuilding"] = json!(true);
        save["openForceAttackResource"] = json!(true);
        save["openForceAttackArea"] = json!(true);
        save["openForceAttackBasement"] = json!(true);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_weather_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(
            200,
            &json!({
                "nowWeather": field_or(save, "nowWeather", json!(0)),
                "weatherLastTime": field_or(save, "weatherLastTime", json!(0)),
            }),
        )
    })
}

fn handle_save_weather_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        apply_field(save, &body, "nowWeather", FT::I);
        apply_field(save, &body, "weatherLastTime", FT::F);
        json_resp(200, &json!({"success": true}))
    })
}

fn handle_save_missions_finished() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(200, &save.get("missionFinished").cloned().unwrap_or(json!([])))
    })
}

fn handle_save_tutorials_finished() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(200, &save.get("tutorialFinished").cloned().unwrap_or(json!([])))
    })
}

fn handle_save_spe_enhance_stone_get() -> (u16, &'static str, Vec<u8>) {
    with_state(|state| {
        let save = match &state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        json_resp(
            200,
            &json!({"speEnhanceStone": field_or(save, "speEnhanceStone", json!(0))}),
        )
    })
}

fn handle_save_spe_enhance_stone_put(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let body = body_json(req);
    with_state(|state| {
        let save = match &mut state.save_data {
            Some(s) => s,
            None => return (400, "application/json", json_err("Save存档未加载")),
        };
        apply_field(save, &body, "speEnhanceStone", FT::I);
        json_resp(200, &json!({"success": true}))
    })
}

// ========== 路由 ==========

fn parse_id(seg: &str) -> Result<i64, (u16, &'static str, Vec<u8>)> {
    seg.parse::<i64>()
        .map_err(|_| (400, "application/json", json_err("无效的ID")))
}

fn api_route(req: &Request, segs: &[&str]) -> (u16, &'static str, Vec<u8>) {
    let m = req.method.as_str();
    match segs {
        ["api", "status"] if m == "GET" => handle_status(),
        ["api", "save_folder"] if m == "POST" => handle_save_folder(req),
        ["api", "browse_folders"] if m == "GET" => handle_browse_folders(req),
        ["api", "save_slots"] if m == "GET" => handle_save_slots(),
        ["api", "load"] if m == "POST" => handle_load(req),

        ["api", "save", "load"] if m == "POST" => handle_save_load(req),
        ["api", "save", "status"] if m == "GET" => handle_save_status(),
        ["api", "save", "world_time"] if m == "GET" => handle_save_world_time_get(),
        ["api", "save", "world_time"] if m == "PUT" => handle_save_world_time_put(req),
        ["api", "save", "game_settings"] if m == "GET" => handle_save_game_settings_get(),
        ["api", "save", "game_settings"] if m == "PUT" => handle_save_game_settings_put(req),
        ["api", "save", "month_limits"] if m == "GET" => handle_save_month_limits_get(),
        ["api", "save", "month_limits"] if m == "PUT" => handle_save_month_limits_put(req),
        ["api", "save", "reset_month_limits"] if m == "POST" => handle_save_reset_month_limits(),
        ["api", "save", "statistics"] if m == "GET" => handle_save_statistics_get(),
        ["api", "save", "statistics"] if m == "PUT" => handle_save_statistics_put(req),
        ["api", "save", "areas"] if m == "GET" => handle_save_areas(),
        ["api", "save", "area", id] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_area_detail(id)
        }
        ["api", "save", "area", id] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_area_update(req, id)
        }
        ["api", "save", "area", id, "buildings"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_area_buildings(id)
        }
        ["api", "save", "area", id, "building", tile] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            let tile = match tile.parse::<usize>() {
                Ok(v) => v,
                Err(_) => return (400, "application/json", json_err("无效的地块索引")),
            };
            handle_save_area_building_update(req, id, tile)
        }
        ["api", "save", "area", id, "buildings", "batch"] if m == "POST" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_area_buildings_batch(req, id)
        }
        ["api", "save", "forces"] if m == "GET" => handle_save_forces(),
        ["api", "save", "force", id] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_force_detail(id)
        }
        ["api", "save", "force", id] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_force_update(req, id)
        }
        ["api", "save", "force", id, "favor"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_force_favor(id)
        }
        ["api", "save", "force", id, "favor"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_force_favor_update(req, id)
        }
        ["api", "save", "resource_points"] if m == "GET" => handle_save_resource_points(),
        ["api", "save", "resource_point", id] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_resource_point_detail(id)
        }
        ["api", "save", "resource_point", id] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_save_resource_point_update(req, id)
        }
        ["api", "save", "prison"] if m == "GET" => handle_save_prison_get(),
        ["api", "save", "prison"] if m == "PUT" => handle_save_prison_put(req),
        ["api", "save", "govern_storage"] if m == "GET" => handle_save_govern_storage_get(),
        ["api", "save", "govern_storage"] if m == "PUT" => handle_save_govern_storage_put(req),
        ["api", "save", "unlock_flags"] if m == "GET" => handle_save_unlock_flags_get(),
        ["api", "save", "unlock_flags"] if m == "PUT" => handle_save_unlock_flags_put(req),
        ["api", "save", "unlock_all"] if m == "POST" => handle_save_unlock_all(),
        ["api", "save", "weather"] if m == "GET" => handle_save_weather_get(),
        ["api", "save", "weather"] if m == "PUT" => handle_save_weather_put(req),
        ["api", "save", "missions_finished"] if m == "GET" => handle_save_missions_finished(),
        ["api", "save", "tutorials_finished"] if m == "GET" => handle_save_tutorials_finished(),
        ["api", "save", "spe_enhance_stone"] if m == "GET" => handle_save_spe_enhance_stone_get(),
        ["api", "save", "spe_enhance_stone"] if m == "PUT" => handle_save_spe_enhance_stone_put(req),
        ["api", "save", "save"] if m == "POST" => handle_save_file_save(),
        ["api", "save"] if m == "POST" => handle_save(),

        ["api", "heroes"] if m == "GET" => handle_heroes(),
        ["api", "heroes", "favor"] if m == "GET" => handle_heroes_favor(),
        ["api", "heroes", "favor", "batch"] if m == "POST" => handle_heroes_favor_batch(req),
        ["api", "hero", id] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_detail(id)
        }
        ["api", "hero", id, "details"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_details(id)
        }
        ["api", "hero", id, "detail_attr"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_detail_attr(req, id)
        }
        ["api", "hero", id, "attr"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_attr(req, id)
        }
        ["api", "hero", id, "basic"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_basic(req, id)
        }
        ["api", "hero", id, "fight-skill"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_fight_living(req, id, "fight")
        }
        ["api", "hero", id, "living-skill"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_fight_living(req, id, "living")
        }
        ["api", "hero", id, "status"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_status(req, id)
        }
        ["api", "hero", id, "fame"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_fame(req, id)
        }
        ["api", "hero", id, "money"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_money(req, id)
        }
        ["api", "hero", id, "force"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_force(id)
        }
        ["api", "hero", id, "force"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_force_update(req, id)
        }
        ["api", "hero", id, "force_contributions"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_force_contributions(id)
        }
        ["api", "hero", id, "force_contributions"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_force_contributions_update(req, id)
        }
        ["api", "hero", id, "talents"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_talents(id)
        }
        ["api", "hero", id, "talents"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_talents_update(req, id)
        }
        ["api", "hero", id, "talent"] if m == "POST" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_talent_add(req, id)
        }
        ["api", "hero", id, "talent"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_talent_put(req, id)
        }
        ["api", "hero", id, "talent", tag] if m == "DELETE" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            let tag = match parse_id(tag) { Ok(v) => v, Err(e) => return e };
            handle_hero_talent_delete(id, tag)
        }
        ["api", "hero", id, "skills"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_skills(id)
        }
        ["api", "hero", id, "skill", idx] if m == "GET" => {
            let (id, idx) = match (parse_id(id), idx.parse::<usize>()) {
                (Ok(a), Ok(b)) => (a, b),
                _ => return (400, "application/json", json_err("无效的参数")),
            };
            handle_skill_detail(id, idx)
        }
        ["api", "hero", id, "skill", idx] if m == "PUT" => {
            let (id, idx) = match (parse_id(id), idx.parse::<usize>()) {
                (Ok(a), Ok(b)) => (a, b),
                _ => return (400, "application/json", json_err("无效的参数")),
            };
            handle_skill_update(req, id, idx)
        }
        ["api", "hero", id, "skill", idx] if m == "DELETE" => {
            let (id, idx) = match (parse_id(id), idx.parse::<usize>()) {
                (Ok(a), Ok(b)) => (a, b),
                _ => return (400, "application/json", json_err("无效的参数")),
            };
            handle_skill_delete(id, idx)
        }
        ["api", "hero", id, "skill"] if m == "POST" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_skill_add(req, id)
        }
        ["api", "hero", id, "action"] if m == "POST" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_action(req, id)
        }
        ["api", "hero", id, "items"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_items(id)
        }
        ["api", "hero", id, "item", idx] if m == "GET" => {
            let (id, idx) = match (parse_id(id), idx.parse::<usize>()) {
                (Ok(a), Ok(b)) => (a, b),
                _ => return (400, "application/json", json_err("无效的参数")),
            };
            handle_hero_item_detail(id, idx)
        }
        ["api", "hero", id, "item", idx] if m == "PUT" => {
            let (id, idx) = match (parse_id(id), idx.parse::<usize>()) {
                (Ok(a), Ok(b)) => (a, b),
                _ => return (400, "application/json", json_err("无效的参数")),
            };
            handle_hero_item_update(req, id, idx)
        }
        ["api", "hero", id, "item", idx] if m == "DELETE" => {
            let (id, idx) = match (parse_id(id), idx.parse::<usize>()) {
                (Ok(a), Ok(b)) => (a, b),
                _ => return (400, "application/json", json_err("无效的参数")),
            };
            handle_hero_item_delete(id, idx)
        }
        ["api", "hero", id, "item"] if m == "POST" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_item_add(req, id)
        }
        ["api", "hero", id, "items", "batch"] if m == "POST" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_items_batch(req, id)
        }
        ["api", "hero", id, "relations"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_relations(id)
        }
        ["api", "hero", id, "relations"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_relations_update(req, id)
        }
        ["api", "hero", id, "favor"] if m == "GET" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_favor(id)
        }
        ["api", "hero", id, "favor"] if m == "PUT" => {
            let id = match parse_id(id) { Ok(v) => v, Err(e) => return e };
            handle_hero_favor_update(req, id)
        }
        ["api", "batch", "action"] if m == "POST" => handle_batch_action(req),
        ["api", "skills", "search"] if m == "GET" => handle_skills_search(req),
        ["api", "attrs", "search"] if m == "GET" => handle_attrs_search(req),
        ["api", "tags", "search"] if m == "GET" => handle_tags_search(req),
        ["api", "items", "types"] if m == "GET" => handle_items_types(),
        ["api", "backup"] if m == "POST" => handle_backup(),
        _ => (404, "application/json", json_err("未找到")),
    }
}

fn route(req: &Request) -> (u16, &'static str, Vec<u8>) {
    let method = req.method.as_str();
    let path = req.path.as_str();
    if method == "GET" {
        if path == "/" || path == "/index.html" {
            return html_resp(200, index_html());
        }
        if path == "/world" || path == "/world.html" {
            return html_resp(200, world_html());
        }
    }
    let segs: Vec<&str> = path.split('/').filter(|s| !s.is_empty()).collect();
    if segs.first() == Some(&"api") {
        return api_route(req, &segs);
    }
    (404, "application/json", json_err("未找到"))
}

fn handle_connection(mut stream: TcpStream) {
    let req = match parse_request(&mut stream) {
        Some(r) => r,
        None => return,
    };
    let (status, content_type, body) = route(&req);
    let resp = build_response(status, content_type, &body);
    let _ = stream.write_all(&resp);
    let _ = stream.flush();
}

// ========== 初始化 ==========

fn init_state() {
    let mut skill_names = BTreeMap::new();
    if let Ok(Value::Object(map)) = serde_json::from_str::<Value>(&inflate_str(SKILL_BIN)) {
        for (k, v) in map {
            if let Ok(id) = k.parse::<i64>() {
                skill_names.insert(id, v);
            }
        }
    }
    let mut spe_attr_map = BTreeMap::new();
    if let Ok(Value::Object(map)) = serde_json::from_str::<Value>(SPE_ATTR_MAP_JSON) {
        for (k, v) in map {
            if let Some(name) = v.as_str() {
                spe_attr_map.insert(k, name.to_string());
            }
        }
    }
    let mut talent_names = BTreeMap::new();
    if let Ok(Value::Object(map)) = serde_json::from_str::<Value>(TALENT_NAMES_JSON) {
        for (k, v) in map {
            if let Ok(id) = k.parse::<i64>() {
                talent_names.insert(id, v);
            }
        }
    }
    let mut tag_names = BTreeMap::new();
    if let Ok(Value::Object(map)) = serde_json::from_str::<Value>(&inflate_str(TAG_BIN)) {
        for (k, v) in map {
            if let Ok(id) = k.parse::<i64>() {
                tag_names.insert(id, v);
            }
        }
    }
    let save_folder = if Path::new(DEFAULT_SAVE_FOLDER).is_dir() {
        Some(DEFAULT_SAVE_FOLDER.to_string())
    } else {
        None
    };
    let _ = STATE.set(Mutex::new(State {
        hero_data: None,
        hero_filepath: "Hero".to_string(),
        save_data: None,
        save_filepath: "Save".to_string(),
        save_folder,
        skill_names,
        spe_attr_map,
        talent_names,
        tag_names,
    }));
}

fn parse_port() -> u16 {
    let args: Vec<String> = std::env::args().collect();
    let mut i = 0;
    while i < args.len() {
        let a = &args[i];
        if a == "--port" && i + 1 < args.len() {
            if let Ok(p) = args[i + 1].parse::<u16>() {
                return p;
            }
        }
        if let Some(v) = a.strip_prefix("--port=") {
            if let Ok(p) = v.parse::<u16>() {
                return p;
            }
        }
        i += 1;
    }
    if let Ok(v) = std::env::var("PORT") {
        if let Ok(p) = v.parse::<u16>() {
            return p;
        }
    }
    5000
}

fn open_browser(port: u16) {
    std::thread::spawn(move || {
        std::thread::sleep(Duration::from_millis(1500));
        let url = format!("http://localhost:{}", port);
        #[cfg(windows)]
        {
            let _ = std::process::Command::new("cmd")
                .args(["/C", "start", ""])
                .arg(&url)
                .spawn();
        }
        #[cfg(not(windows))]
        {
            let _ = std::process::Command::new("xdg-open").arg(&url).spawn();
        }
    });
}

fn main() {
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            let _ = std::env::set_current_dir(dir);
        }
    }

    init_state();

    let port = parse_port();

    println!("==================================================");
    println!("  龙胤立志传 - Web 存档修改器 (Rust 版)");
    println!("==================================================");
    println!();
    println!("  服务器地址: http://localhost:{}", port);
    println!("  按 Ctrl+C 停止服务器");
    println!();

    let detected = STATE.get().map(|m| m.lock().unwrap().save_folder.is_some()).unwrap_or(false);
    if detected {
        println!("  已检测到默认存档目录: {}", DEFAULT_SAVE_FOLDER);
        println!("  在网页界面中选择存档槽位 (SaveSlot) 即可加载存档");
        println!();
    } else {
        println!("  [提示] 未检测到默认 Steam 存档目录 ({})", DEFAULT_SAVE_FOLDER);
        println!("  [提示] 请在网页界面点击 \"选择存档目录\" 手动指定");
        println!();
    }

    open_browser(port);

    let addr = format!("127.0.0.1:{}", port);
    let listener = match TcpListener::bind(&addr) {
        Ok(l) => l,
        Err(e) => {
            eprintln!("无法绑定端口 {}: {}", port, e);
            std::process::exit(1);
        }
    };

    for stream in listener.incoming() {
        match stream {
            Ok(s) => {
                let _ = s.set_read_timeout(Some(Duration::from_secs(30)));
                std::thread::spawn(move || handle_connection(s));
            }
            Err(_) => continue,
        }
    }
}
