import flet as ft
import os
import json
import subprocess

# Cấu hình Alignment cố định
ALIGN_CENTER = ft.Alignment(0, 0)


def main(page: ft.Page):
    # Cấu hình phông chữ chuyên nghiệp
    page.fonts = {
        "Montserrat": "https://fonts.gstatic.com/s/montserrat/v25/JTUSjIg1_i6t8kCHKm459Wlhyw.ttf",
        "OpenSans": "https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.ttf"
    }

    page.title = "Animal Pro - Folder Based Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1550
    page.window_height = 950
    page.padding = 20
    page.theme = ft.Theme(font_family="OpenSans")

    DATA_FILE = "data_studio.json"
    all_rows_data = []
    entries_container = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    # Ô nhập nhạc nền tổng
    bg_music_input = ft.TextField(
        label="Nhạc nền (vd: Splashing Around - The Green Orbs.mp3)",
        value="Splashing Around - The Green Orbs.mp3",
        width=500,
        border_color="blue"
    )

    def save_data(e=None):
        data_to_save = {
            "format": format_selector.value,
            "bg_music": bg_music_input.value,
            "rows": []
        }
        for r in all_rows_data:
            data_to_save["rows"].append({
                "folder": r["folder"].value,
                "files": r["files"].value,
                "title": r["title"].value,
                "desc": r["desc"].value,
                "note": r["note"].value,
                "voice": r["voice"].value,
                "theme": r["theme"].value
            })
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def on_change_handler(e):
        save_data()

    def create_animal_row(folder_val="", file_val="", title_val="", desc_val="", note_val="", voice_val="Nữ",
                          theme_val="Rừng"):
        f_folder = ft.TextField(label="Thư mục", width=80, value=folder_val, border_color="blue")
        f_files = ft.TextField(label="Tệp (vd: 1.jpg, 2.mp4)", expand=2, value=file_val, border_color="orange")
        f_title = ft.TextField(label="Tiêu đề", width=150, value=title_val)
        f_desc = ft.TextField(label="Giới thiệu", expand=3, value=desc_val)
        f_note = ft.TextField(label="Ghi chú", width=120, value=note_val)

        f_voice = ft.Dropdown(
            label="Giọng", width=90, value=voice_val,
            options=[ft.dropdown.Option("Nam"), ft.dropdown.Option("Nữ")]
        )

        f_theme = ft.Dropdown(
            label="Tông", width=100, value=theme_val,
            options=[ft.dropdown.Option("Rừng"), ft.dropdown.Option("Biển"), ft.dropdown.Option("Sa mạc"),
                     ft.dropdown.Option("Tuyết")]
        )

        for ctrl in [f_folder, f_files, f_title, f_desc, f_note, f_voice, f_theme]:
            ctrl.on_change = on_change_handler

        row_content = ft.Row([
            f_folder, f_files, f_title, f_desc, f_note, f_voice, f_theme,
            ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red400",
                          on_click=lambda _: remove_row(row_container))
        ])

        row_container = ft.Container(content=row_content, padding=10, border=ft.Border.all(1, ft.Colors.WHITE12),
                                     border_radius=12, bgcolor=ft.Colors.WHITE10)
        row_entry = {"folder": f_folder, "files": f_files, "title": f_title, "desc": f_desc, "note": f_note,
                     "voice": f_voice, "theme": f_theme, "ui": row_container}
        all_rows_data.append(row_entry)
        return row_container

    def remove_row(ui_element):
        for r in all_rows_data:
            if r["ui"] == ui_element:
                all_rows_data.remove(r)
                break
        entries_container.controls.remove(ui_element)
        save_data()
        page.update()

    def add_more(e):
        entries_container.controls.append(create_animal_row(folder_val=str(len(all_rows_data) + 1)))
        save_data()
        page.update()

    format_selector = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="horizontal", label="🎬 Ngang"),
            ft.Radio(value="vertical", label="📱 Dọc"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
        value="horizontal"
    )
    format_selector.on_change = on_change_handler

    def load_saved_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                format_selector.value = data.get("format", "horizontal")
                bg_music_input.value = data.get("bg_music", "Splashing Around - The Green Orbs.mp3")
                for r_data in data.get("rows", []):
                    entries_container.controls.append(create_animal_row(
                        r_data.get("folder", ""), r_data.get("files", ""),
                        r_data.get("title", ""), r_data.get("desc", ""),
                        r_data.get("note", ""), r_data.get("voice", "Nữ"),
                        r_data.get("theme", "Rừng")
                    ))
                return True
            except Exception:
                pass
        return False

    if not load_saved_data():
        for i in range(1, 3): entries_container.controls.append(create_animal_row(folder_val=str(i)))

    def generate_html_content():
        is_vertical = format_selector.value == "vertical"
        items_js = []
        theme_map = {"Rừng": "#4CAF50", "Biển": "#00BCD4", "Sa mạc": "#FFC107", "Tuyết": "#E0F7FA"}

        for r in all_rows_data:
            folder = r["folder"].value.strip()
            raw_files = r["files"].value.strip()
            if raw_files and r["title"].value:
                # 1. Xác định danh sách media từ ô nhập liệu
                file_list = [f.strip() for f in raw_files.split(',') if f.strip()]
                media_data = []
                for f in file_list:
                    is_vid = f.lower().endswith(('.mp4', '.webm', '.mov'))
                    path = f"assets/{folder}/{f}" if folder else f"assets/{f}"
                    media_data.append({"src": path, "type": "video" if is_vid else "image"})

                # 2. Logic tìm Thumbnail TỰ ĐỘNG trong thư mục vật lý
                final_thumb = ""
                folder_path = os.path.join("assets", folder) if folder else "assets"

                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    try:
                        files_in_folder = os.listdir(folder_path)
                        # Tìm file có chữ thumbnail (như thumbnail2.jpg của bạn)
                        for f in files_in_folder:
                            if "thumbnail" in f.lower():
                                final_thumb = f"assets/{folder}/{f}" if folder else f"assets/{f}"
                                break

                        # Nếu chưa tìm thấy, tìm ảnh đầu tiên bất kỳ
                        if not final_thumb:
                            for f in files_in_folder:
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                    final_thumb = f"assets/{folder}/{f}" if folder else f"assets/{f}"
                                    break
                    except Exception:
                        pass

                # Fallback cuối cùng nếu folder không có ảnh nào
                if not final_thumb and media_data:
                    final_thumb = media_data[0]["src"]

                if media_data:
                    items_js.append({
                        "media": media_data,
                        "thumb": final_thumb,
                        "title": r["title"].value.strip(),
                        "desc": r["desc"].value.strip(),
                        "note": r["note"].value.strip(),
                        "voice": r["voice"].value,
                        "color": theme_map.get(r["theme"].value, "#ffffff")
                    })

        size_title = "50px" if is_vertical else "80px"
        pos_left = "30px" if is_vertical else "80px"
        width_content = "85%" if is_vertical else "750px"

        # Kích thước thumbnail dạng Portrait (đứng)
        thumb_w, thumb_h = ("80px", "120px") if is_vertical else ("140px", "210px")

        return f'''
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{ margin: 0; background: #000; font-family: 'Open Sans', sans-serif; overflow: hidden; }}
                .container {{ width: 100vw; height: 100vh; {"max-width: 600px; margin: auto;" if is_vertical else ""} position: relative; }}
                .item {{ position: absolute; width: 100%; height: 100%; display: none; }}
                .item.active {{ display: block; }}

                .media-layer {{ width: 100%; height: 100%; object-fit: cover; position: absolute; transition: opacity 1s; opacity: 0; }}
                .media-layer.visible {{ opacity: 1; }}

                .overlay {{ position: absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(to right, rgba(0,0,0,0.85), transparent, rgba(0,0,0,0.85)); z-index: 5; }}

                .content {{ 
                    position: absolute; top: 50%; left: {pos_left}; transform: translateY(-50%); 
                    color: #fff; z-index: 100; width: {width_content}; padding: 40px;
                    border-radius: 25px; background: rgba(0,0,0,0.4); backdrop-filter: blur(15px);
                    border: 1px solid rgba(255,255,255,0.15); display: none;
                }}
                .item.active .content {{ display: block; animation: showContent 0.8s ease-out forwards; }}

                .name {{ font-family: 'Montserrat'; font-size: {size_title}; font-weight: 900; text-transform: uppercase; line-height: 1.1; margin-bottom: 20px; text-shadow: 4px 4px 15px #000; }}
                .des {{ font-size: 22px; color: #eee; margin-bottom: 25px; line-height: 1.6; font-weight: 400; }}
                .note-box {{ font-family: 'Montserrat'; font-weight: 800; font-size: 32px; text-transform: uppercase; letter-spacing: 1px; }}

                /* THANH THUMBNAIL */
                .thumbnails {{ 
                    position: absolute; bottom: 40px; right: 40px; 
                    display: flex; gap: 15px; z-index: 200; 
                    justify-content: flex-end; align-items: flex-end; flex-wrap: nowrap;
                }}
                .thumb {{ 
                    width: {thumb_w}; height: {thumb_h}; border-radius: 12px; 
                    background-size: cover; background-position: center; background-color: #1a1a1a;
                    border: 2px solid rgba(255,255,255,0.3); transition: 0.4s; 
                    opacity: 0.4; cursor: pointer;
                }}
                .thumb:hover {{ opacity: 0.8; transform: translateY(-5px); border-color: #fff; }}
                .thumb.active {{ opacity: 1; border-color: orange; transform: scale(1.1) translateY(-10px); box-shadow: 0 15px 40px rgba(255,165,0,0.6); }}

                /* NÚT ĐIỀU HƯỚNG */
                .nav-btns {{ position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); display: flex; gap: 30px; z-index: 210; }}
                .nav-btn {{ 
                    width: 75px; height: 75px; border-radius: 50%; border: 3px solid #fff; 
                    background: rgba(0,0,0,0.4); color: #fff; font-size: 32px; cursor: pointer; 
                    display: flex; align-items: center; justify-content: center; transition: 0.3s;
                    backdrop-filter: blur(10px);
                }}
                .nav-btn:hover {{ background: orange; color: #000; border-color: orange; transform: scale(1.15); box-shadow: 0 0 20px rgba(255,165,0,0.4); }}
                .nav-btn:active {{ transform: scale(0.9); }}

                #start-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.97); z-index: 999; display: flex; align-items: center; justify-content: center; }}
                #start-btn {{ padding: 30px 80px; font-family: 'Montserrat'; font-size: 30px; font-weight: 900; background: orange; color: #000; border: none; border-radius: 60px; cursor: pointer; transition: 0.3s; box-shadow: 0 10px 40px rgba(255,165,0,0.3); }}
                #start-btn:hover {{ transform: scale(1.05); background: #fff; }}

                @keyframes showContent {{ from {{ opacity: 0; transform: translate(-30px, -50%); }} to {{ opacity: 1; transform: translate(0, -50%); }} }}
            </style>
        </head>
        <body>
            <div id="start-overlay"><button id="start-btn">BẮT ĐẦU TRẢI NGHIỆM</button></div>
            <audio id="bg-music" loop src="assets/{bg_music_input.value}"></audio>

            <div class="container" id="main-slide"></div>

            <div class="nav-btns">
                <div class="nav-btn" onclick="prevSlide()">❮</div>
                <div class="nav-btn" onclick="nextSlide()">❯</div>
            </div>

            <div class="thumbnails" id="thumb-bar"></div>

            <script>
                const data = {json.dumps(items_js)};
                let slideIndex = 0;
                let subMediaIndex = 0;
                const synth = window.speechSynthesis;
                const bgMusic = document.getElementById('bg-music');
                let voices = [];
                let mediaInterval;
                let autoSlideTimeout;

                function init() {{
                    const slideCont = document.getElementById('main-slide');
                    const thumbCont = document.getElementById('thumb-bar');
                    data.forEach((item, i) => {{
                        const slide = document.createElement('div');
                        slide.className = `item ${{i===0?'active':''}}`;

                        item.media.forEach((m, mi) => {{
                            if(m.type === 'video') {{
                                const vid = document.createElement('video');
                                vid.className = `media-layer ${{mi===0?'visible':''}}`;
                                vid.muted = true;
                                vid.playsInline = true;
                                vid.loop = true;
                                vid.src = m.src;
                                slide.appendChild(vid);
                            }} else {{
                                const img = document.createElement('div');
                                img.className = `media-layer ${{mi===0?'visible':''}}`;
                                img.style.backgroundImage = `url('${{m.src}}')`;
                                img.style.backgroundSize = 'cover';
                                img.style.backgroundPosition = 'center';
                                slide.appendChild(img);
                            }}
                        }});

                        slide.innerHTML += `
                            <div class="overlay"></div>
                            <div class="content">
                                <div class="name" style="border-left: 15px solid ${{item.color}}; padding-left: 25px;">${{item.title}}</div>
                                <div class="des">${{item.desc}}</div>
                                <div class="note-box" style="color: ${{item.color}}">${{item.note}}</div>
                            </div>`;
                        slideCont.appendChild(slide);

                        // Tạo Thumbnail với hình ảnh tự động nhận diện
                        const thumb = document.createElement('div');
                        thumb.className = `thumb ${{i===0?'active':''}}`;
                        thumb.style.backgroundImage = `url('${{item.thumb}}')`;
                        thumb.onclick = () => jumpToSlide(i);
                        thumbCont.appendChild(thumb);
                    }});
                    updateVoices();
                }}

                function updateVoices() {{
                    voices = synth.getVoices();
                }}
                if (speechSynthesis.onvoiceschanged !== undefined) {{
                    speechSynthesis.onvoiceschanged = updateVoices;
                }}

                function cycleMedia() {{
                    const currentSlide = document.querySelectorAll('.item')[slideIndex];
                    const layers = currentSlide.querySelectorAll('.media-layer');
                    if(layers.length <= 1) return;

                    layers[subMediaIndex].classList.remove('visible');
                    if(layers[subMediaIndex].tagName === 'VIDEO') layers[subMediaIndex].pause();

                    subMediaIndex = (subMediaIndex + 1) % layers.length;
                    layers[subMediaIndex].classList.add('visible');
                    if(layers[subMediaIndex].tagName === 'VIDEO') layers[subMediaIndex].play();
                }}

                function speak(item) {{
                    synth.cancel();
                    clearInterval(mediaInterval);
                    clearTimeout(autoSlideTimeout);
                    subMediaIndex = 0;

                    const text = `${{item.title}}. ${{item.desc}}. ${{item.note}}`;
                    const utter = new SpeechSynthesisUtterance(text);
                    utter.lang = 'vi-VN';
                    utter.volume = 1.0; 
                    utter.rate = 0.85;

                    const viVoices = voices.filter(v => v.lang.toLowerCase().includes('vi'));
                    if (viVoices.length > 0) {{
                        const nameKey = item.voice === 'Nam' ? ['an', 'nam', 'minh', 'hung'] : ['hoai', 'linh', 'nhi', 'chi'];
                        utter.voice = viVoices.find(v => nameKey.some(k => v.name.toLowerCase().includes(k))) || viVoices[0];
                    }}

                    mediaInterval = setInterval(cycleMedia, 6000);

                    synth.speak(utter);
                    utter.onend = () => {{
                        clearInterval(mediaInterval);
                        autoSlideTimeout = setTimeout(nextSlide, 5000);
                    }};
                }}

                function updateActiveUI(index) {{
                    const slides = document.querySelectorAll('.item');
                    const thumbs = document.querySelectorAll('.thumb');

                    slides.forEach(s => {{
                        s.classList.remove('active');
                        s.querySelectorAll('video').forEach(v => v.pause());
                    }});
                    thumbs.forEach(t => t.classList.remove('active'));

                    slideIndex = index;
                    const nextSlideElem = slides[slideIndex];
                    nextSlideElem.classList.add('active');
                    thumbs[slideIndex].classList.add('active');

                    const layers = nextSlideElem.querySelectorAll('.media-layer');
                    layers.forEach((l, idx) => {{
                        if(idx === 0) {{
                            l.classList.add('visible');
                            if(l.tagName === 'VIDEO') l.play();
                        }} else {{
                            l.classList.remove('visible');
                            if(l.tagName === 'VIDEO') l.pause();
                        }}
                    }});
                    speak(data[slideIndex]);
                }}

                function nextSlide() {{
                    let nextIdx = (slideIndex + 1) % data.length;
                    updateActiveUI(nextIdx);
                }}

                function prevSlide() {{
                    let prevIdx = (slideIndex - 1 + data.length) % data.length;
                    updateActiveUI(prevIdx);
                }}

                function jumpToSlide(index) {{
                    updateActiveUI(index);
                }}

                document.getElementById('start-btn').onclick = () => {{
                    document.getElementById('start-overlay').style.display = 'none';
                    bgMusic.volume = 0.08; 
                    bgMusic.play();
                    updateActiveUI(0);
                }};

                init();
            </script>
        </body>
        </html>
        '''

    def deploy(e):
        save_data()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(generate_html_content())
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Fixed Thumbnails and improved Nav buttons"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            page.snack_bar = ft.SnackBar(ft.Text("Đã sửa lỗi Thumbnail và cập nhật lên GitHub!"))
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi: {ex}"))
            page.snack_bar.open = True
        page.update()

    def preview_local(e):
        save_data()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(generate_html_content())
        try:
            os.startfile(os.path.abspath("index.html"))
        except:
            subprocess.run(["open", os.path.abspath("index.html")])

    page.add(
        ft.Column([
            ft.Container(content=ft.Text("ANIMAL STUDIO - FIXED NAV & THUMBS", size=30, weight="bold", color="orange"),
                         alignment=ALIGN_CENTER),
            bg_music_input,
            format_selector,
            entries_container,
            ft.Row([
                ft.FilledButton("THÊM DÒNG", icon=ft.Icons.ADD, on_click=add_more),
                ft.FilledButton("XEM TRỰC TIẾP", icon=ft.Icons.PREVIEW, on_click=preview_local, bgcolor="green"),
                ft.FilledButton("ĐẨY LÊN GITHUB", icon=ft.Icons.UPLOAD, on_click=deploy, bgcolor="blue", width=350,
                                height=60)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], expand=True)
    )


if __name__ == "__main__":
    ft.run(main)