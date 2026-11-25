"""Generate EJI static site: English at root (default), Indonesian under /id/."""
import os, sys

OUT = sys.argv[1]
T = lambda s: f'<span class="todo">{s}</span>'

ADDRESS = "Indy Bintaro Office Park, Building A, 5th Floor<br>Jl. Boulevard Bintaro Jaya Blok B7/A6<br>South Tangerang 15424, Indonesia"
ADDRESS_INLINE = "Indy Bintaro Office Park, Building A, 5th Floor, Jl. Boulevard Bintaro Jaya Blok B7/A6, South Tangerang 15424, Indonesia"
EMAIL = '<a href="mailto:cs@electrajaringan.co.id">cs@electrajaringan.co.id</a>'
PHONE = "021 3007 7878"

L = {
 "en": dict(
  lang="en", banner="DRAFT. Items highlighted in yellow must be confirmed before launch.",
  tagline="ALVA charging network operator",
  nav=[("index.html#services","Services"),("index.html#how-it-works","How It Works"),("index.html#contact","Contact")],
  title="PT Electra Jaringan Indonesia | Electric Motorcycle Charging",
  desc="PT Electra Jaringan Indonesia operates the ALVA charging network for electric motorcycles. Pay per kWh by QRIS or GoPay.",
  tnc="Terms and Conditions", refund="Cancellation and Refund", privacy="Privacy Policy",
  tnc_file="terms.html", privacy_file="privacy.html",
  footer_about="ALVA charging stations are operated by PT Electra Jaringan Indonesia, holder of an Electricity Supply Business License (IUPTL).",
  footer_services="Services", footer_policies="Policies", rights="All rights reserved.", home="Home",
 ),
 "id": dict(
  lang="id", banner="DRAFT. Teks bertanda kuning wajib dikonfirmasi sebelum tayang.",
  tagline="Operator jaringan pengisian daya ALVA",
  nav=[("index.html#layanan","Layanan"),("index.html#cara-pakai","Cara Pakai"),("index.html#kontak","Kontak")],
  title="PT Electra Jaringan Indonesia | Pengisian Daya Motor Listrik",
  desc="PT Electra Jaringan Indonesia mengoperasikan jaringan pengisian daya ALVA untuk motor listrik. Bayar per kWh lewat QRIS atau GoPay.",
  tnc="Syarat dan Ketentuan", refund="Pembatalan dan Pengembalian Dana", privacy="Kebijakan Privasi",
  tnc_file="syarat-ketentuan.html", privacy_file="kebijakan-privasi.html",
  footer_about="Stasiun pengisian daya ALVA dioperasikan oleh PT Electra Jaringan Indonesia, pemegang Izin Usaha Penyediaan Tenaga Listrik (IUPTL).",
  footer_services="Layanan", footer_policies="Kebijakan", rights="Hak cipta dilindungi.", home="Beranda",
 ),
}
# counterpart page names for the language switch
PAIR = {"index.html":"index.html","terms.html":"syarat-ketentuan.html","privacy.html":"kebijakan-privasi.html"}
PAIR.update({v:k for k,v in list(PAIR.items())})


def page(lg, fname, title, body):
    c = L[lg]; pre = "" if lg == "en" else "../"
    en_href = (pre + (fname if lg == "en" else PAIR[fname]))
    id_href = ("id/" + PAIR[fname]) if lg == "en" else fname
    nav = "\n".join(f'      <a href="{h}">{t}</a>' for h, t in c["nav"])
    return f'''<!doctype html>
<html lang="{lg}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{c["desc"]}">
<link rel="icon" href="{pre}assets/logo-alva-black.png">
<link rel="stylesheet" href="{pre}assets/style.css">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html">
      <img src="{pre}assets/logo-alva-white.png" alt="">
      <span>Electra Jaringan Indonesia<small>{c["tagline"]}</small></span>
    </a>
    <div class="header-right">
      <nav class="nav" aria-label="Main">
{nav}
      </nav>
      <div class="lang" aria-label="Language">
        <a href="{en_href}" hreflang="en" aria-current="{str(lg=="en").lower()}">EN</a><span>|</span><a href="{id_href}" hreflang="id" aria-current="{str(lg=="id").lower()}">ID</a>
      </div>
    </div>
  </div>
</header>

{body}

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html"><img src="{pre}assets/logo-alva-white.png" alt=""><span>Electra Jaringan Indonesia</span></a>
        <p style="margin-top:12px">{c["footer_about"]}</p>
      </div>
      <div>
        <div class="footer-title">{c["footer_services"]}</div>
        <ul>
{chr(10).join(f'          <li><a href="{h}">{t}</a></li>' for h, t in c["nav"])}
        </ul>
      </div>
      <div>
        <div class="footer-title">{c["footer_policies"]}</div>
        <ul>
          <li><a href="{c["tnc_file"]}">{c["tnc"]}</a></li>
          <li><a href="{c["tnc_file"]}#refund">{c["refund"]}</a></li>
          <li><a href="{c["privacy_file"]}">{c["privacy"]}</a></li>
        </ul>
      </div>
    </div>
    <div class="copyright">&copy; 2026 PT Electra Jaringan Indonesia. {c["rights"]}</div>
  </div>
</footer>

</body>
</html>
'''

# ---------------- HOME ----------------
HOME = {
"en": f'''<main>
  <section class="hero">
    <div class="wrap">
      <span class="eyebrow">Electric motorcycle charging</span>
      <h1>Charge your electric motorcycle. Pay only for the kWh you use.</h1>
      <p>PT Electra Jaringan Indonesia (EJI) holds an Electricity Supply Business License (IUPTL) and operates the ALVA charging network. Plug in, charge, and settle one daily bill by QRIS or GoPay.</p>
      <div class="actions">
        <a class="btn btn-app" href="#how-it-works">How it works</a>
        <a class="btn btn-ghost" href="#contact">Contact us</a>
      </div>
    </div>
  </section>

  <section id="services">
    <div class="wrap">
      <div class="section-head">
        <h2>Our service</h2>
        <p class="lead">We sell electricity for charging battery electric two-wheelers at our stations.</p>
      </div>
      <div class="grid grid-3">
        <div class="card">
          <div class="icon"><img src="assets/ev-plug-charging.svg" alt=""></div>
          <h3>Charging stations</h3>
          <p>1,037 charging connectors across the ALVA network (November 2026), ready for ALVA electric motorcycles.</p>
        </div>
        <div class="card">
          <div class="icon"><img src="assets/Money.svg" alt=""></div>
          <h3>Pay per kWh</h3>
          <p>You pay for the energy delivered to your vehicle, as recorded by the station meter. Rates are itemised in your daily bill.</p>
        </div>
        <div class="card">
          <div class="icon"><img src="assets/smartphone-device.svg" alt=""></div>
          <h3>One daily digital bill</h3>
          <p>All charging sessions in a day are combined into one bill, sent by email and paid online.</p>
        </div>
      </div>
    </div>
  </section>

  <section id="how-it-works" class="alt">
    <div class="wrap">
      <div class="section-head">
        <h2>How it works</h2>
        <p class="lead">Register once, then just plug in and charge.</p>
      </div>
      <div class="grid grid-4">
        <div class="card"><span class="step-no">1</span><h3>Register once</h3><p>Register your vehicle and accept the Terms and Conditions in the My ALVA app.</p></div>
        <div class="card"><span class="step-no">2</span><h3>Plug in and charge</h3><p>Plug in at any EJI station. The energy delivered is recorded automatically for each session.</p></div>
        <div class="card"><span class="step-no">3</span><h3>Get your bill</h3><p>Your daily bill is issued at 00:10 WIB and sent to your registered email, with kWh and charges per session.</p></div>
        <div class="card"><span class="step-no">4</span><h3>Pay</h3><p>Pay by QRIS or GoPay from the link in your bill. A QRIS code is valid for 15 minutes and can be regenerated.</p></div>
      </div>

      <h3 style="margin-top:48px">Payment methods</h3>
      <div class="pay-list" aria-label="Accepted payment methods">
        <span class="pay">QRIS</span>
        <span class="pay">GoPay</span>
      </div>
      <div class="inline-message">Payments are processed by Midtrans as our payment gateway. EJI does not store your card details, PIN, or e-wallet password.</div>
    </div>
  </section>

  <section id="contact" class="contact">
    <div class="wrap">
      <div class="section-head">
        <h2>Contact</h2>
        <p class="lead">Questions about bills, payments, or a station issue.</p>
      </div>
      <div class="grid grid-2">
        <div class="card"><dl>
          <div><dt>Company</dt><dd>PT Electra Jaringan Indonesia</dd></div>
          <div><dt>Address</dt><dd>{ADDRESS}</dd></div>
        </dl></div>
        <div class="card"><dl>
          <div><dt>Customer service email</dt><dd>{EMAIL}</dd></div>
          <div><dt>Phone</dt><dd>{PHONE}</dd></div>
        </dl></div>
      </div>
    </div>
  </section>
</main>''',
"id": f'''<main>
  <section class="hero">
    <div class="wrap">
      <span class="eyebrow">Pengisian daya motor listrik</span>
      <h1>Isi daya motor listrik, bayar sesuai kWh yang dipakai.</h1>
      <p>PT Electra Jaringan Indonesia (EJI) adalah pemegang Izin Usaha Penyediaan Tenaga Listrik (IUPTL) yang mengoperasikan jaringan pengisian daya ALVA. Cukup colok, isi daya, lalu bayar satu tagihan harian lewat QRIS atau GoPay.</p>
      <div class="actions">
        <a class="btn btn-app" href="#cara-pakai">Cara pakai</a>
        <a class="btn btn-ghost" href="#kontak">Hubungi kami</a>
      </div>
    </div>
  </section>

  <section id="layanan">
    <div class="wrap">
      <div class="section-head">
        <h2>Layanan kami</h2>
        <p class="lead">Penjualan tenaga listrik untuk pengisian daya kendaraan listrik roda dua berbasis baterai di stasiun kami.</p>
      </div>
      <div class="grid grid-3">
        <div class="card">
          <div class="icon"><img src="../assets/ev-plug-charging.svg" alt=""></div>
          <h3>Stasiun pengisian daya</h3>
          <p>1.037 konektor pengisian daya di jaringan ALVA (November 2026), siap dipakai motor listrik ALVA.</p>
        </div>
        <div class="card">
          <div class="icon"><img src="../assets/Money.svg" alt=""></div>
          <h3>Bayar per kWh</h3>
          <p>Biaya dihitung dari energi yang masuk ke kendaraan, tercatat oleh meter stasiun. Rincian tarif tercantum di tagihan harian.</p>
        </div>
        <div class="card">
          <div class="icon"><img src="../assets/smartphone-device.svg" alt=""></div>
          <h3>Satu tagihan harian digital</h3>
          <p>Semua sesi pengisian dalam sehari digabung jadi satu tagihan, dikirim ke email dan dibayar secara online.</p>
        </div>
      </div>
    </div>
  </section>

  <section id="cara-pakai" class="alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Cara pakai dan bayar</h2>
        <p class="lead">Daftar sekali, setelah itu cukup colok dan isi daya.</p>
      </div>
      <div class="grid grid-4">
        <div class="card"><span class="step-no">1</span><h3>Daftar sekali</h3><p>Daftarkan kendaraan dan setujui Syarat dan Ketentuan di aplikasi My ALVA.</p></div>
        <div class="card"><span class="step-no">2</span><h3>Colok dan isi daya</h3><p>Colokkan kendaraan di stasiun EJI. Energi yang masuk tercatat otomatis per sesi.</p></div>
        <div class="card"><span class="step-no">3</span><h3>Terima tagihan</h3><p>Tagihan harian terbit pukul 00.10 WIB dan dikirim ke email terdaftar, berisi rincian kWh dan biaya per sesi.</p></div>
        <div class="card"><span class="step-no">4</span><h3>Bayar</h3><p>Bayar lewat QRIS atau GoPay dari tautan di tagihan. Kode QRIS berlaku 15 menit dan bisa dibuat ulang.</p></div>
      </div>

      <h3 style="margin-top:48px">Metode pembayaran</h3>
      <div class="pay-list" aria-label="Metode pembayaran yang diterima">
        <span class="pay">QRIS</span>
        <span class="pay">GoPay</span>
      </div>
      <div class="inline-message">Pembayaran diproses oleh Midtrans sebagai payment gateway. EJI tidak menyimpan data kartu, PIN, atau kata sandi e-wallet Anda.</div>
    </div>
  </section>

  <section id="kontak" class="contact">
    <div class="wrap">
      <div class="section-head">
        <h2>Kontak</h2>
        <p class="lead">Pertanyaan soal tagihan, pembayaran, atau kendala di stasiun.</p>
      </div>
      <div class="grid grid-2">
        <div class="card"><dl>
          <div><dt>Perusahaan</dt><dd>PT Electra Jaringan Indonesia</dd></div>
          <div><dt>Alamat</dt><dd>{ADDRESS.replace("South Tangerang","Tangerang Selatan").replace("Building A, 5th Floor","Gedung A, Lantai 5")}</dd></div>
        </dl></div>
        <div class="card"><dl>
          <div><dt>Email layanan pelanggan</dt><dd>{EMAIL}</dd></div>
          <div><dt>Telepon</dt><dd>{PHONE}</dd></div>
        </dl></div>
      </div>
    </div>
  </section>
</main>''',
}

ADDR_ID = ADDRESS_INLINE.replace("South Tangerang","Tangerang Selatan").replace("Building A, 5th Floor","Gedung A, Lantai 5")

# ---------------- TERMS ----------------
TERMS = {
"en": f'''<main class="legal"><div class="wrap"><article class="doc">
  <h1>Terms and Conditions</h1>
  <p class="meta">Effective from 25 November 2026</p>

  <h2>1. Parties</h2>
  <p>These Terms and Conditions govern the use of charging stations operated by PT Electra Jaringan Indonesia ("EJI") by registered users ("User"). By registering and using a station, the User confirms that they have read and accepted these terms.</p>

  <h2>2. Registration</h2>
  <p>Users register their vehicle and an active email address in the My ALVA app. Acceptance of these terms is given once and applies to all later sessions. Users are responsible for the accuracy of the data they register.</p>

  <h2>3. Use of stations</h2>
  <ul>
    <li>Stations may only be used to charge compatible vehicles, following the instructions on site.</li>
    <li>The energy recorded by the station meter is the basis for billing.</li>
    <li>Users must report station damage or problems to customer service.</li>
  </ul>

  <h2>4. Rates and billing</h2>
  <p>Charges are calculated per kWh of energy delivered, plus applicable taxes. Applicable rates are itemised in each daily bill. All sessions in one calendar day are combined into one bill, issued at 00:10 WIB the next day and sent to the User's email. EJI may change its rates with at least 7 days' notice.</p>

  <h2>5. Payment</h2>
  <p>Bills are paid by QRIS or GoPay, processed by Midtrans. One payment settles one bill. A QRIS code is valid for 15 minutes; if it expires, the User can generate a new one from the bill link. Unpaid bills may lead to charging access being suspended until the bill is settled.</p>

  <h2 id="refund">6. Cancellation and refund</h2>
  <p>Charging that has already taken place cannot be cancelled. A refund is given if:</p>
  <ul>
    <li>the User has paid the same bill more than once; or</li>
    <li>there is an error in the recorded kWh or bill calculation, confirmed by EJI.</li>
  </ul>
  <p>Complaints must be sent to customer service within 7 days of the bill date, with the bill number and proof of payment. Approved refunds are returned to the original payment method or the User's bank account within 14 business days.</p>

  <h2>7. Limitation of liability</h2>
  <p>EJI works to keep stations operational but does not guarantee that every station is available at all times. EJI is not liable for losses caused by use of a station contrary to its instructions, or by events beyond EJI's reasonable control.</p>

  <h2>8. Changes to these terms</h2>
  <p>EJI may update these terms. The latest version is always available on this page, and material changes are announced to the registered email.</p>

  <h2>9. Governing law</h2>
  <p>These terms are governed by the laws of the Republic of Indonesia. Disputes are first settled amicably and, failing that, through the competent district court in Indonesia.</p>

  <h2>10. Contact</h2>
  <p>PT Electra Jaringan Indonesia, {ADDRESS_INLINE}. Email {EMAIL}, phone {PHONE}.</p>
</article></div></main>''',
"id": f'''<main class="legal"><div class="wrap"><article class="doc">
  <h1>Syarat dan Ketentuan</h1>
  <p class="meta">Berlaku sejak 25 November 2026</p>

  <h2>1. Para pihak</h2>
  <p>Syarat dan Ketentuan ini mengatur penggunaan stasiun pengisian daya yang dioperasikan oleh PT Electra Jaringan Indonesia ("EJI") oleh pengguna terdaftar ("Pengguna"). Dengan mendaftar dan memakai stasiun, Pengguna dianggap telah membaca dan menyetujui ketentuan ini.</p>

  <h2>2. Pendaftaran</h2>
  <p>Pengguna mendaftarkan kendaraan dan alamat email aktif melalui aplikasi My ALVA. Persetujuan atas ketentuan ini cukup diberikan satu kali dan berlaku untuk semua sesi berikutnya. Pengguna bertanggung jawab atas kebenaran data yang didaftarkan.</p>

  <h2>3. Penggunaan stasiun</h2>
  <ul>
    <li>Stasiun hanya digunakan untuk mengisi daya kendaraan yang kompatibel, sesuai petunjuk di lokasi.</li>
    <li>Energi yang tercatat oleh meter stasiun menjadi dasar perhitungan tagihan.</li>
    <li>Pengguna wajib melaporkan kerusakan atau kendala stasiun ke layanan pelanggan.</li>
  </ul>

  <h2>4. Tarif dan tagihan</h2>
  <p>Biaya dihitung per kWh energi yang masuk ke kendaraan, ditambah pajak yang berlaku. Rincian tarif tercantum di setiap tagihan harian. Semua sesi dalam satu hari kalender digabung menjadi satu tagihan yang terbit pukul 00.10 WIB keesokan harinya dan dikirim ke email Pengguna. EJI dapat mengubah tarif dengan pemberitahuan paling lambat 7 hari sebelum berlaku.</p>

  <h2>5. Pembayaran</h2>
  <p>Tagihan dibayar melalui QRIS atau GoPay yang diproses oleh Midtrans. Satu pembayaran melunasi satu tagihan. Kode QRIS berlaku 15 menit; jika kedaluwarsa, Pengguna dapat membuat kode baru dari tautan tagihan. Tagihan yang belum dibayar dapat menyebabkan akses pengisian daya ditangguhkan sampai tagihan dilunasi.</p>

  <h2 id="refund">6. Pembatalan dan pengembalian dana</h2>
  <p>Layanan pengisian daya yang sudah terjadi tidak dapat dibatalkan. Pengembalian dana diberikan jika:</p>
  <ul>
    <li>Pengguna terbukti membayar lebih dari satu kali untuk tagihan yang sama; atau</li>
    <li>terdapat kesalahan pencatatan kWh atau perhitungan tagihan yang dikonfirmasi oleh EJI.</li>
  </ul>
  <p>Keluhan diajukan ke layanan pelanggan paling lambat 7 hari sejak tagihan terbit, dengan menyertakan nomor tagihan dan bukti pembayaran. Pengembalian dana yang disetujui dikirim ke metode pembayaran asal atau rekening Pengguna dalam 14 hari kerja.</p>

  <h2>7. Batasan tanggung jawab</h2>
  <p>EJI berupaya menjaga stasiun tetap berfungsi, namun tidak menjamin ketersediaan stasiun setiap saat. EJI tidak bertanggung jawab atas kerugian akibat penggunaan stasiun yang tidak sesuai petunjuk, atau gangguan di luar kendali wajar EJI.</p>

  <h2>8. Perubahan ketentuan</h2>
  <p>EJI dapat memperbarui ketentuan ini. Versi terbaru selalu tersedia di halaman ini, dan perubahan penting diberitahukan melalui email terdaftar.</p>

  <h2>9. Hukum yang berlaku</h2>
  <p>Ketentuan ini tunduk pada hukum Republik Indonesia. Sengketa diselesaikan secara musyawarah terlebih dahulu, dan jika tidak tercapai, melalui pengadilan negeri yang berwenang di Indonesia.</p>

  <h2>10. Kontak</h2>
  <p>PT Electra Jaringan Indonesia, {ADDR_ID}. Email {EMAIL}, telepon {PHONE}.</p>
</article></div></main>''',
}

# ---------------- PRIVACY ----------------
PRIV = {
"en": f'''<main class="legal"><div class="wrap"><article class="doc">
  <h1>Privacy Policy</h1>
  <p class="meta">Effective from 25 November 2026</p>

  <h2>Data we collect</h2>
  <ul>
    <li>Identity and contact data: name, email, phone number.</li>
    <li>Vehicle data: the vehicle identification number (VIN) of registered vehicles.</li>
    <li>Usage data: station location, session time, and kWh delivered.</li>
    <li>Transaction data: bill number, amount, payment method and status. Card details, PINs, and e-wallet passwords are processed by Midtrans and are not stored by EJI.</li>
  </ul>

  <h2>How we use it</h2>
  <p>We use this data to calculate and send bills, process payments, handle complaints and refunds, keep the service secure, and meet our reporting obligations to regulators.</p>

  <h2>Sharing</h2>
  <p>EJI shares data only with parties needed to run the service: our payment gateway (Midtrans), ALVA group affiliates that support operations, and government authorities where required by law. EJI does not sell personal data.</p>

  <h2>Retention and security</h2>
  <p>Data is kept while the account is active and for as long as tax and electricity regulations require, and is then deleted or anonymised. EJI applies reasonable technical and organisational safeguards in line with Law No. 27 of 2022 on Personal Data Protection.</p>

  <h2>Your rights</h2>
  <p>You may request access to, correction of, or deletion of your personal data by contacting {EMAIL}. Requests are processed within the time required by applicable law.</p>

  <h2>Contact</h2>
  <p>PT Electra Jaringan Indonesia, {ADDRESS_INLINE}.</p>
</article></div></main>''',
"id": f'''<main class="legal"><div class="wrap"><article class="doc">
  <h1>Kebijakan Privasi</h1>
  <p class="meta">Berlaku sejak 25 November 2026</p>

  <h2>Data yang kami kumpulkan</h2>
  <ul>
    <li>Data identitas dan kontak: nama, email, nomor telepon.</li>
    <li>Data kendaraan: nomor rangka (VIN) kendaraan yang didaftarkan.</li>
    <li>Data pemakaian: lokasi stasiun, waktu sesi, dan jumlah kWh.</li>
    <li>Data transaksi: nomor tagihan, nominal, metode dan status pembayaran. Data kartu, PIN, atau kata sandi e-wallet diproses oleh Midtrans dan tidak disimpan oleh EJI.</li>
  </ul>

  <h2>Tujuan penggunaan</h2>
  <p>Data digunakan untuk menghitung dan mengirim tagihan, memproses pembayaran, menangani keluhan dan pengembalian dana, menjaga keamanan layanan, serta memenuhi kewajiban pelaporan kepada regulator.</p>

  <h2>Pembagian data</h2>
  <p>EJI hanya membagikan data kepada pihak yang diperlukan untuk menjalankan layanan: penyedia payment gateway (Midtrans), afiliasi grup ALVA yang mendukung operasional, dan instansi pemerintah jika diwajibkan oleh hukum. EJI tidak menjual data pribadi Pengguna.</p>

  <h2>Penyimpanan dan keamanan</h2>
  <p>Data disimpan selama akun aktif dan selama diwajibkan oleh peraturan perpajakan dan ketenagalistrikan, lalu dihapus atau dianonimkan. EJI menerapkan pengamanan teknis dan organisasi yang wajar sesuai Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi.</p>

  <h2>Hak Pengguna</h2>
  <p>Pengguna dapat meminta akses, perbaikan, atau penghapusan data pribadi dengan menghubungi {EMAIL}. Permintaan diproses dalam jangka waktu sesuai ketentuan yang berlaku.</p>

  <h2>Kontak</h2>
  <p>PT Electra Jaringan Indonesia, {ADDR_ID}.</p>
</article></div></main>''',
}

def write(path, html):
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    open(full, "w").write(html)

for lg in ("en", "id"):
    c = L[lg]; d = "" if lg == "en" else "id/"
    write(d + "index.html", page(lg, "index.html", c["title"], HOME[lg]))
    write(d + c["tnc_file"], page(lg, c["tnc_file"], f'{c["tnc"]} | PT Electra Jaringan Indonesia', TERMS[lg]))
    write(d + c["privacy_file"], page(lg, c["privacy_file"], f'{c["privacy"]} | PT Electra Jaringan Indonesia', PRIV[lg]))
print("ok")
