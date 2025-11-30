import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import re
import time

# Load token dari bot.env
load_dotenv('bot.env')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

class URLShortener:
    def shorten_url(self, long_url, provider, custom_alias=None):
        """Shorten URL dengan provider tertentu dan custom alias"""
        try:
            if provider == 'click_ru':
                response = requests.get(f"https://clck.ru/--?url={long_url}", timeout=10)
                if response.status_code == 200 and response.text.strip():
                    return response.text.strip()
                return None
            
            elif provider == 'da_gd':
                response = requests.get(f"https://da.gd/s?url={long_url}", timeout=10)
                return response.text.strip() if response.status_code == 200 else None
            
            elif provider == 'osdb_link':
                response = requests.post("https://osdb.link/", 
                                       data={"url": long_url},
                                       headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                       timeout=10)
                
                if response.status_code == 200:
                    html_content = response.text
                    label_match = re.search(r'<label id=surl>.*?(http://osdb\.link/\w+)', html_content)
                    if label_match:
                        return label_match.group(1)
                    url_match = re.search(r'http://osdb\.link/[\w]+', html_content)
                    if url_match:
                        return url_match.group(0)
                return None
            
            elif provider == 'is_gd':
                if custom_alias:
                    # Gunakan format JSON untuk custom alias
                    url = f"https://is.gd/create.php?format=json&url={long_url}&shorturl={custom_alias}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'shorturl' in data:
                            return data['shorturl']
                        elif 'errorcode' in data:
                            return f"ERROR:{data['errorcode']}:{data['errormessage']}"
                    return None
                else:
                    response = requests.get(f"https://is.gd/create.php?format=simple&url={long_url}", timeout=10)
                    return response.text.strip() if response.status_code == 200 else None
            
            elif provider == 'v_gd':
                if custom_alias:
                    # Gunakan format JSON untuk custom alias
                    url = f"https://v.gd/create.php?format=json&url={long_url}&shorturl={custom_alias}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'shorturl' in data:
                            return data['shorturl']
                        elif 'errorcode' in data:
                            return f"ERROR:{data['errorcode']}:{data['errormessage']}"
                    return None
                else:
                    response = requests.get(f"https://v.gd/create.php?format=simple&url={long_url}", timeout=10)
                    return response.text.strip() if response.status_code == 200 else None
            
            elif provider == 'tinyurl':
                response = requests.get(f"https://tinyurl.com/api-create.php?url={long_url}", timeout=10)
                if response.status_code == 200 and response.text.strip():
                    short_url = response.text.strip()
                    return short_url if short_url.startswith('http') else f"https://{short_url}"
                return None
            
        except Exception as e:
            print(f"Error dengan {provider}: {e}")
            return None
        
        return None

# Initialize shortener
shortener = URLShortener()

# Dictionary untuk simpan URL sementara
user_urls = {}
user_custom_data = {}  # Untuk simpan data custom alias
user_batch_urls = {}   # Untuk simpan batch URLs

# Statistics
bot_stats = {
    'start_time': time.time(),
    'urls_shortened': 0,
    'users_served': set()
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    bot_stats['users_served'].add(user_id)
    
    await update.message.reply_text(
        "🤖 URL Shortener Bot\n\n"
        "Kirim URL yang ingin dipendekkan:\n"
        "• google.com\n" 
        "• https://example.com\n"
        "• http://website.com\n\n"
        "🎯 Fitur:\n"
        "• /custom - Custom alias\n"
        "• /batch - Shorten 5 URL sekaligus\n\n"
        "📋 Gunakan /help untuk melihat semua command"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 Daftar Command Bot

🔹 /start - Memulai bot dan menampilkan pesan selamat datang
🔹 /help - Menampilkan pesan bantuan ini
🔹 /stats - Menampilkan statistik penggunaan bot
🔹 /providers - Menampilkan daftar provider URL shortener
🔹 /about - Tentang bot ini dan developer
🔹 /ping - Cek status dan respon time bot
🔹 /custom - Buat shortlink dengan custom alias
🔹 /batch - Shorten 5 URL sekaligus

💡 Cara Penggunaan:
1. Kirim URL langsung ke bot
2. Atau gunakan /custom <url> <alias> untuk custom shortlink
3. Atau gunakan /batch untuk multiple URLs
4. Pilih provider yang diinginkan
5. Dapatkan URL pendek!

🔗 Contoh URL:
• google.com
• https://github.com
• http://example.com

🎯 Custom Alias:
• /custom google.com mysearch
• /custom https://github.com rirozo_github

📦 Batch URLs:
• /batch lalu kirim 5 URL (dipisah newline)
"""
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime_seconds = time.time() - bot_stats['start_time']
    uptime_str = format_uptime(uptime_seconds)
    
    stats_text = f"""
📊 Statistik Bot

👥 Total Pengguna: {len(bot_stats['users_served'])}
🔗 URL Dipendekkan: {bot_stats['urls_shortened']}
⏰ Uptime: {uptime_str}
🔄 Provider Tersedia: 6
🎯 Fitur Custom: Tersedia
📦 Fitur Batch: Tersedia (5 URLs)

📈 Provider Paling Populer:
• clck.ru - Cepat & Andal
• tinyurl.com - Legacy & Terpercaya
• is.gd - Simple & Clean (Support Custom Alias)
"""
    await update.message.reply_text(stats_text)

async def providers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    providers_text = """
🛠 Daftar Provider URL Shortener

✅ Support Custom Alias:
🔹 (is.gd) - Minimalis, tanpa iklan dan analytics
🔹 (v.gd) - Versi custom dari is.gd

🔹 Semua Provider:
🔹 (clck.ru) - Provider Rusia, cepat dan andal
🔹 (da.gd) - Simple dan clean, tanpa tracking
🔹 (osdb.link) - Open Source database link shortener  
🔹 (is.gd) - Minimalis, tanpa iklan & analytics
🔹 (v.gd) - Versi custom dari is.gd
🔹 (tinyurl.com) - Legacy, terpercaya sejak 2002

⭐ Custom Alias: Gunakan is.gd atau v.gd
🎯 Format Alias: huruf, angka, underscore (_)
📦 Batch: Support semua provider
"""
    await update.message.reply_text(providers_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """
🤖 Tentang URL Shortener Bot

📝 Deskripsi:
Bot Telegram untuk memendekkan URL dengan berbagai provider gratis. 
Mendukung 6 provider terbaik dengan hasil instan.

⚡ Fitur:
• 6 Provider URL Shortener
• Custom Alias Support
• Batch URL Shortening (5 URLs)
• Pilihan Provider untuk Custom Link
• Proses Cepat & Real-time
• Interface User-friendly  
• Gratis 100%

👨‍💻 Developer: SEO RIROZO

🆘 Butuh Bantuan? Gunakan /help
"""
    await update.message.reply_text(about_text, disable_web_page_preview=True)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    message = await update.message.reply_text("🏓 Pong!")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 2)
    
    await message.edit_text(f"🏓 Pong!\n⏱ Response Time: `{ping_time}ms`\n🟢 Status: Online")

async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle batch URL shortening command"""
    await update.message.reply_text(
        "📦 Batch URL Shortening\n\n"
        "Kirim 5 URL yang ingin dipendekkan (maksimal 5 URL):\n"
        "• Pisahkan dengan newline/enter\n"
        "• Boleh dengan atau tanpa http/https\n\n"
        "📝 Contoh:\n"
        "google.com\n"
        "https://github.com\n"
        "example.com\n"
        "http://python.org\n"
        "stackoverflow.com\n\n"
        "⏳ Akan saya proses dengan provider pilihan Anda..."
    )
    
    # Set state untuk menunggu batch URLs
    user_id = update.message.from_user.id
    user_batch_urls[user_id] = {'waiting_for_batch': True}

async def handle_batch_urls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle batch URLs input dari user"""
    user_id = update.message.from_user.id
    
    # Cek apakah user dalam mode batch
    if user_id not in user_batch_urls or not user_batch_urls[user_id].get('waiting_for_batch'):
        return
    
    text = update.message.text.strip()
    urls = [url.strip() for url in text.split('\n') if url.strip()]
    
    # Validasi jumlah URL
    if len(urls) > 5:
        await update.message.reply_text(
            "❌ Terlalu banyak URL. Maksimal 5 URL.\n"
            "Silakan gunakan /batch lagi dan kirim maksimal 5 URL."
        )
        del user_batch_urls[user_id]
        return
    
    if len(urls) < 1:
        await update.message.reply_text(
            "❌ Tidak ada URL yang valid.\n"
            "Silakan gunakan /batch lagi dan kirim URL yang valid."
        )
        del user_batch_urls[user_id]
        return
    
    # Validasi dan proses URLs
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        # Validasi URL dasar
        if not any(proto in url for proto in ['http://', 'https://', '.', ':']):
            invalid_urls.append(url)
            continue
        
        # Auto tambah https jika perlu
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        valid_urls.append(url)
    
    if invalid_urls:
        await update.message.reply_text(
            f"❌ {len(invalid_urls)} URL tidak valid:\n" +
            "\n".join(f"• {url}" for url in invalid_urls) +
            "\n\nHanya URL valid yang akan diproses."
        )
    
    if not valid_urls:
        await update.message.reply_text("❌ Tidak ada URL yang valid untuk diproses.")
        del user_batch_urls[user_id]
        return
    
    # Simpan batch URLs dan tampilkan pilihan provider
    user_batch_urls[user_id] = {
        'urls': valid_urls[:5],  # Maksimal 5 URL
        'waiting_for_batch': False
    }
    
    # Buat keyboard pilihan provider untuk batch
    keyboard = [
        [
            InlineKeyboardButton("🔗 clck.ru", callback_data="batch_click_ru"),
            InlineKeyboardButton("🔗 da.gd", callback_data="batch_da_gd")
        ],
        [
            InlineKeyboardButton("🔗 osdb.link", callback_data="batch_osdb_link"),
            InlineKeyboardButton("🔗 is.gd", callback_data="batch_is_gd")
        ],
        [
            InlineKeyboardButton("🔗 v.gd", callback_data="batch_v_gd"),
            InlineKeyboardButton("🔗 tinyurl.com", callback_data="batch_tinyurl")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    url_list = "\n".join([f"• {url}" for url in valid_urls[:5]])
    
    await update.message.reply_text(
        f"📦 Batch URLs ({len(valid_urls)} URL):\n{url_list}\n\n"
        "Pilih provider untuk semua URL:",
        reply_markup=reply_markup
    )

async def handle_batch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback untuk batch URL shortening"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    # Dapatkan batch data user
    batch_data = user_batch_urls.get(user_id)
    
    if not batch_data or 'urls' not in batch_data:
        await query.edit_message_text("❌ Data batch tidak ditemukan. Gunakan /batch lagi.")
        return
    
    urls = batch_data['urls']
    provider = callback_data.replace('batch_', '')  # Hapus prefix 'batch_'
    
    # Provider names untuk display
    provider_names = {
        'click_ru': 'clck.ru',
        'da_gd': 'da.gd',
        'osdb_link': 'osdb.link',
        'is_gd': 'is.gd',
        'v_gd': 'v.gd',
        'tinyurl': 'tinyurl.com'
    }
    
    provider_name = provider_names.get(provider, provider)
    
    await query.edit_message_text(f"⏳ Memendekkan {len(urls)} URL dengan {provider_name}...")
    
    # Process semua URLs
    results = []
    successful_count = 0
    
    for i, url in enumerate(urls, 1):
        short_url = shortener.shorten_url(url, provider)
        
        if short_url and short_url.startswith(('http://', 'https://')):
            results.append(f"{i}. ✅ {short_url}")
            successful_count += 1
            bot_stats['urls_shortened'] += 1
        else:
            results.append(f"{i}. ❌ Gagal: {url}")
    
    # Format hasil
    result_text = f"📦 Hasil Batch Shortening ({provider_name})\n\n"
    result_text += "\n".join(results)
    result_text += f"\n\n📊 Statistik: {successful_count}/{len(urls)} berhasil"
    
    if successful_count < len(urls):
        result_text += "\n💡 Beberapa URL gagal, coba provider lain."
    
    await query.edit_message_text(result_text)
    
    # Hapus data batch setelah selesai
    if user_id in user_batch_urls:
        del user_batch_urls[user_id]

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom alias command: /custom <url> <alias>"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Format: /custom <url> <alias>\n\n"
            "📝 Contoh:\n"
            "• /custom https://google.com mysearch\n"
            "• /custom google.com rirozo_page\n"
            "• /custom example.com my_page123\n\n"
            "📋 Aturan alias:\n"
            "• Hanya huruf, angka, underscore (_)\n"
            "• Minimal 3 karakter\n"
            "• Tidak boleh spasi atau karakter khusus\n"
            "• Auto convert ke lowercase"
        )
        return
    
    url = context.args[0]
    custom_alias = context.args[1].lower()  # Auto lowercase
    
    # Validasi URL
    if not any(proto in url for proto in ['http://', 'https://', '.', ':']):
        url = 'https://' + url
    
    # Validasi custom alias
    if len(custom_alias) < 3:
        await update.message.reply_text("❌ Alias terlalu pendek. Minimal 3 karakter.")
        return
    
    if not re.match(r'^[a-z0-9_]+$', custom_alias):
        await update.message.reply_text(
            "❌ Format alias tidak valid.\n"
            "Hanya boleh menggunakan:\n"
            "• Huruf kecil (a-z)\n" 
            "• Angka (0-9)\n"
            "• Underscore (_)\n\n"
            "✅ Contoh: my_page, link123, rirozo_site\n"
            "❌ Contoh: my-page, MyPage, link@123"
        )
        return
    
    # Simpan data user untuk custom alias
    user_id = update.message.from_user.id
    user_custom_data[user_id] = {
        'url': url,
        'alias': custom_alias
    }
    
    # Buat keyboard pilihan provider untuk custom alias
    keyboard = [
        [
            InlineKeyboardButton("🔗 is.gd", callback_data="custom_is_gd"),
            InlineKeyboardButton("🔗 v.gd", callback_data="custom_v_gd")
        ],
        [
            InlineKeyboardButton("📋 Lihat Provider Lain", callback_data="custom_more_info")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎯 Custom Alias: `{custom_alias}`\n"
        f"🔗 URL: `{url}`\n\n"
        "Pilih provider untuk custom alias:\n"
        "• is.gd - Recommended\n"
        "• v.gd - Alternative",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_custom_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback untuk custom alias provider selection"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    # Dapatkan data custom user
    custom_data = user_custom_data.get(user_id)
    
    if not custom_data:
        await query.edit_message_text("❌ Data custom alias tidak ditemukan. Gunakan /custom lagi.")
        return
    
    url = custom_data['url']
    custom_alias = custom_data['alias']
    
    # Map callback ke provider
    provider_map = {
        'custom_is_gd': 'is_gd',
        'custom_v_gd': 'v_gd'
    }
    
    if callback_data == 'custom_more_info':
        # Tampilkan info provider
        await query.edit_message_text(
            "ℹ️ Provider Support Custom Alias:\n\n"
            "✅ is.gd - Recommended\n"
            "• Format: https://is.gd/alias_anda\n"
            "• Minimalis & cepat\n"
            "• Tanpa iklan & analytics\n\n"
            "✅ v.gd - Alternative\n"
            "• Format: https://v.gd/alias_anda\n"
            "• Sama seperti is.gd\n"
            "• Backup option\n\n"
            "❌ Provider lain tidak support custom alias\n"
            "Gunakan /custom lagi untuk memilih provider."
        )
        return
    
    provider = provider_map.get(callback_data)
    
    if not provider:
        await query.edit_message_text("❌ Provider tidak valid.")
        return
    
    # Provider names untuk display
    provider_names = {
        'is_gd': 'is.gd',
        'v_gd': 'v.gd'
    }
    
    await query.edit_message_text(f"⏳ Membuat custom link dengan {provider_names[provider]}...")
    
    # Shorten dengan custom alias
    short_url = shortener.shorten_url(url, provider, custom_alias)
    
    # Update statistics
    if short_url and short_url.startswith('http'):
        bot_stats['urls_shortened'] += 1
    
    if short_url and short_url.startswith('http'):
        # Success
        await query.edit_message_text(
            f"✅ Custom Alias Berhasil!\n\n"
            f"🔗 {short_url}\n"
            f"📝 Alias: {custom_alias}\n"
            f"🛠 Provider: {provider_names[provider]}\n\n"
            f"💡 Tips: Copy link di atas untuk share!"
        )
    elif short_url and short_url.startswith('ERROR:2:'):
        # Alias already exists
        await query.edit_message_text(
            f"❌ Alias '{custom_alias}' sudah dipakai di {provider_names[provider]}.\n\n"
            f"💡 Coba:\n"
            f"• Pilih provider lain\n"
            f"• Ganti alias: {custom_alias}2, my_{custom_alias}\n"
            f"• Gunakan /custom lagi"
        )
    elif short_url and short_url.startswith('ERROR:'):
        # Other error
        error_msg = short_url.split(':', 2)[2]
        await query.edit_message_text(
            f"❌ Error dengan {provider_names[provider]}:\n{error_msg}\n\n"
            f"💡 Coba provider lain atau ganti alias."
        )
    else:
        await query.edit_message_text(
            f"❌ {provider_names[provider]} gagal membuat custom alias.\n"
            f"Silakan coba provider lain atau gunakan provider biasa."
        )
    
    # Hapus data custom setelah selesai
    if user_id in user_custom_data:
        del user_custom_data[user_id]

def format_uptime(seconds):
    """Format uptime seconds to human readable string"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle single URL input"""
    user_id = update.message.from_user.id
    
    # Cek jika user dalam mode batch
    if user_id in user_batch_urls and user_batch_urls[user_id].get('waiting_for_batch'):
        await handle_batch_urls(update, context)
        return
    
    url = update.message.text.strip()
    
    # Validasi URL
    if not any(proto in url for proto in ['http://', 'https://', '.', ':']):
        await update.message.reply_text("❌ Format URL tidak valid. Pastikan URL mengandung domain (contoh: google.com)")
        return
    
    # Auto tambah https jika perlu
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Simpan URL user
    user_urls[user_id] = url
    
    # Buat keyboard pilihan provider dengan layout 2 kolom
    keyboard = [
        [
            InlineKeyboardButton("🔗 clck.ru", callback_data="click_ru"),
            InlineKeyboardButton("🔗 da.gd", callback_data="da_gd")
        ],
        [
            InlineKeyboardButton("🔗 osdb.link", callback_data="osdb_link"),
            InlineKeyboardButton("🔗 is.gd", callback_data="is_gd")
        ],
        [
            InlineKeyboardButton("🔗 v.gd", callback_data="v_gd"),
            InlineKeyboardButton("🔗 tinyurl.com", callback_data="tinyurl")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📝 URL: `{url}`\n\n"
        "Pilih shortener:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback untuk semua jenis shortening"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    # Handle batch callbacks
    if callback_data.startswith('batch_'):
        await handle_batch_callback(update, context)
        return
    
    # Handle custom alias callbacks
    if callback_data.startswith('custom_'):
        await handle_custom_callback(update, context)
        return
    
    # Handle normal URL shortening callbacks
    provider = callback_data
    
    # Dapatkan URL user
    url = user_urls.get(user_id)
    
    if not url:
        await query.edit_message_text("❌ URL tidak ditemukan. Kirim URL lagi.")
        return
    
    # Provider names untuk display
    provider_names = {
        'click_ru': 'clck.ru',
        'da_gd': 'da.gd',
        'osdb_link': 'osdb.link',
        'is_gd': 'is.gd',
        'v_gd': 'v.gd',
        'tinyurl': 'tinyurl.com'
    }
    
    await query.edit_message_text(f"⏳ Memendekkan dengan {provider_names[provider]}...")
    
    # Shorten URL
    short_url = shortener.shorten_url(url, provider)
    
    # Update statistics
    if short_url:
        bot_stats['urls_shortened'] += 1
    
    if short_url:
        # Validasi hasil
        if short_url.startswith(('http://', 'https://')):
            message = f"""
✅ {provider_names[provider]}

🔗 {short_url}
        """
        else:
            # Jika hasil tidak mengandung http, tambahkan
            if '.' in short_url:
                short_url = f"https://{short_url}"
            message = f"""
✅ {provider_names[provider]}

🔗 {short_url}
        """
        await query.edit_message_text(message)
    else:
        await query.edit_message_text(
            f"❌ {provider_names[provider]} gagal atau sedang down.\n"
            "Silakan coba provider lain."
        )

def main():
    if not TOKEN:
        print("❌ Token tidak ditemukan! Pastikan file bot.env ada")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("providers", providers_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CommandHandler("batch", batch_command))  # ✅ Batch command
    
    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 Bot berjalan...")
    print("📚 Command yang tersedia: /start, /help, /stats, /providers, /about, /ping, /custom, /batch")
    app.run_polling()

if __name__ == '__main__':
    main()