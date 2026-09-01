// build.rs - 编译期压缩内嵌资源，减小最终 exe 体积
use std::env;
use std::fs;
use std::path::PathBuf;

fn main() {
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
