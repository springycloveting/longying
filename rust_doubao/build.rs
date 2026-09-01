// build.rs - 编译期压缩内嵌资源 + 嵌入 Windows 版本资源
use std::env;
use std::fs;
use std::path::PathBuf;

fn main() {
    // 嵌入 Windows 版本资源（仅 Windows 目标）
    if env::var("CARGO_CFG_TARGET_OS").map(|v| v == "windows").unwrap_or(false) {
        let mut res = winresource::WindowsResource::new();
        res.set("FileVersion", "1.1.0")
            .set("ProductVersion", "1.1.0")
            .set("ProductName", "龙胤立志传 - Web 存档修改器")
            .set("FileDescription", "龙胤立志传 - Web 存档修改器 (Rust 版)")
            .set("LegalCopyright", "© 2026");
        let _ = res.compile();
    }

    println!("cargo:rerun-if-changed=assets");
    let out = PathBuf::from(env::var("OUT_DIR").unwrap());

    // (源文件相对 assets 的路径, 输出压缩文件名)
    let files: [(&str, &str); 4] = [
        ("web/index.html", "index.bin"),
        ("web/world.html", "world.bin"),
        ("skill_names.json", "skill.bin"),
        ("tag_names.json", "tag.bin"),
    ];

    for (src, dst) in files {
        let data = fs::read(PathBuf::from("assets").join(src)).expect("read asset");
        let comp = miniz_oxide::deflate::compress_to_vec(&data, 9);
        fs::write(out.join(dst), &comp).expect("write compressed");
        println!(
            "cargo:warning=compressed {}: {} -> {} bytes ({}%)",
            src,
            data.len(),
            comp.len(),
            comp.len() * 100 / data.len()
        );
    }
}
