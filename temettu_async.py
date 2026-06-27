"""
temettu_async.py
----------------
async playwright ile yüksek hızlı temettü/sermaye artırımı kazıyıcı.
600 hisse için tahmini süre: ~15-20 dakika (CONCURRENT_TABS=20 ile)

Kurulum:
  pip install playwright pandas
  playwright install chromium
"""

import asyncio
import json
import time
import random
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright, Page

# ─── Ayarlar ─────────────────────────────────────────────────────────────────
CIKTI_JSON      = "temettu_verileri.json"
HATA_LOG        = "hata_log.json"
CONCURRENT_TABS = 20       # Aynı anda açık tab sayısı — 15-25 arası önerilir
SAYFA_TIMEOUT   = 35000    # Sayfa yükleme timeout (ms) — networkidle için artırıldı
YENIDEN_DENEME  = 2        # Hata durumunda kaç kez tekrar denesin

# ─── Sembol listesi ──────────────────────────────────────────────────────────
# İstersen harici dosyadan oku: semboller = Path("semboller.txt").read_text().split()
SEMBOLLER = [
"A1CAP","A1YEN","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON","AGESA","AGHOL","AGROT","AGYO","AHGAZ","AHSGY","AKBNK","AKCNS","AKENR","AKFGY","AKFIS","AKFYE","AKGRT","AKMGY","AKSA","AKSEN","AKSGY","AKSUE","AKYHO","ALARK","ALBRK","ALCAR","ALCTL","ALFAS","ALGYO","ALKA","ALKIM","ALKLC","ALTINS1","ALTNY","ALVES","ANELE","ANGEN","ANHYT","ANSGR","ARASE","ARCLK","ARDYZ","ARENA","ARMGD","ARSAN","ARTMS","ARZUM","ASELS","ASGYO","ASTOR","ASUZU","ATAGY","ATAKP","ATATP","ATEKS","ATLAS","ATSYH","AVGYO","AVHOL","AVOD","AVPGY","AVTUR","AYCES","AYDEM","AYEN","AYES","AYGAZ","AZTEK","BAGFS","BAHKM","BAKAB","BALAT","BALSU","BANVT","BARMA","BASCM","BASGZ","BAYRK","BEGYO","BERA","BESLR","BEYAZ","BFREN","BIENY","BIGCH","BIGEN","BIMAS","BINBN","BINHO","BIOEN","BIZIM","BJKAS","BLCYT","BMSCH","BMSTL","BNTAS","BOBET","BORLS","BORSK","BOSSA","BRISA","BRKO","BRKSN","BRKVY","BRLSM","BRMEN","BRSAN","BRYAT","BSOKE","BTCIM","BUCIM","BULGS","BURCE","BURVA","BVSAN","BYDNR","CANTE","CASA","CATES","CCOLA","CELHA","CEMAS","CEMTS","CEMZY","CEOEM","CGCAM","CIMSA","CLEBI","CMBTN","CMENT","CONSE","COSMO","CRDFA","CRFSA","CUSAN","CVKMD","CWENE","DAGI","DAPGM","DARDL","DCTTR","DENGE","DERHL","DERIM","DESA","DESPC","DEVA","DGATE","DGGYO","DGNMO","DIRIT","DITAS","DMLKTG","DMRGD","DMSAS","DNISI","DOAS","DOBUR","DOCO","DOFER","DOGUB","DOHOL","DOKTA","DSTKF","DURDO","DURKN","DYOBY","DZGYO","EBEBK","ECILC","ECZYT","EDATA","EDIP","EFORC","EGEEN","EGEGY","EGEPO","EGGUB","EGPRO","EGSER","EKGYO","EKIZ","EKOS","EKSUN","ELITE","EMKEL","EMNIS","ENDAE","ENERY","ENJSA","ENKAI","ENSRI","ENTRA","EPLAS","ERBOS","ERCB","EREGL","ERSU","ESCAR","ESCOM","ESEN","ETILR","ETYAT","EUHOL","EUKYO","EUPWR","EUREN","EUYO","EYGYO","FADE","FENER","FLAP","FMIZP","FONET","FORMT","FORTE","FRIGO","FROTO","FZLGY","GARAN","GARFA","GEDIK","GEDZA","GENIL","GENTS","GEREL","GESAN","GIPTA","GLBMD","GLCVY","GLRMK","GLRYH","GLYHO","GMTAS","GOKNR","GOLTS","GOODY","GOZDE","GRNYO","GRSEL","GRTHO","GSDDE","GSDHO","GSRAY","GUBRF","GUNDG","GWIND","GZNMI","HALKB","HATEK","HATSN","HDFGS","HEDEF","HEKTS","HKTM","HLGYO","HOROZ","HRKET","HTTBT","HUBVC","HUNER","HURGZ","ICBCT","ICUGS","IDGYO","IEYHO","IHAAS","IHEVA","IHGZT","IHLAS","IHLGM","IHYAY","IMASM","INDES","INFO","INGRM","INTEK","INTEM","INVEO","INVES","IPEKE","ISATR","ISBIR","ISBTR","ISCTR","ISDMR","ISFIN","ISGSY","ISGYO","ISKPL","ISKUR","ISMEN","ISSEN","ISYAT","IZENR","IZFAS","IZINV","IZMDC","JANTS","KAPLM","KAREL","KARSN","KARTN","KATMR","KAYSE","KBORU","KCAER","KCHOL","KENT","KERVN","KFEIN","KGYO","KIMMR","KLGYO","KLKIM","KLMSN","KLNMA","KLRHO","KLSER","KLSYN","KLYPV","KMPUR","KNFRT","KOCMT","KONKA","KONTR","KONYA","KOPOL","KORDS","KOTON","KOZAA","KOZAL","KRDMA","KRDMB","KRDMD","KRGYO","KRONT","KRPLS","KRSTL","KRTEK","KRVGD","KSTUR","KTLEV","KTSKR","KUTPO","KUVVA","KUYAS","KZBGY","KZGYO","LIDER","LIDFA","LILAK","LINK","LKMNH","LMKDC","LOGO","LRSHO","LUKSK","LYDHO","LYDYE","MAALT","MACKO","MAGEN","MAKIM","MAKTK","MANAS","MARBL","MARKA","MARTI","MAVI","MEDTR","MEGAP","MEGMT","MEKAG","MEPET","MERCN","MERIT","MERKO","METRO","METUR","MGROS","MHRGY","MIATK","MMCAS","MNDRS","MNDTR","MOBTL","MOGAN","MOPAS","MPARK","MRGYO","MRSHL","MSGYO","MTRKS","MTRYO","MZHLD","NATEN","NETAS","NIBAS","NTGAZ","NTHOL","NUGYO","NUHCM","OBAMS","OBASE","ODAS","ODINE","OFSYM","ONCSM","ONRYT","ORCAY","ORGE","ORMA","OSMEN","OSTIM","OTKAR","OTTO","OYAKC","OYAYO","OYLUM","OYYAT","OZATD","OZGYO","OZKGY","OZRDN","OZSUB","OZYSR","PAGYO","PAMEL","PAPIL","PARSN","PASEU","PATEK","PCILT","PEKGY","PENGD","PENTA","PETKM","PETUN","PGSUS","PINSU","PKART","PKENT","PLTUR","PNLSN","PNSUT","POLHO","POLTK","PRDGS","PRKAB","PRKME","PRZMA","PSDTC","PSGYO","QNBFK","QNBTR","QUAGR","RALYH","RAYSG","REEDR","RGYAS","RNPOL","RODRG","RTALB","RUBNS","RUZYE","RYGYO","RYSAS","SAFKR","SAHOL","SAMAT","SANEL","SANFM","SANKO","SARKY","SASA","SAYAS","SDTTR","SEGMN","SEGYO","SEKFK","SEKUR","SELEC","SELGD","SELVA","SERNT","SEYKM","SILVR","SISE","SKBNK","SKTAS","SKYLP","SKYMD","SMART","SMRTG","SMRVA","SNGYO","SNICA","SNKRN","SNPAM","SODSN","SOKE","SOKM","SONME","SRVGY","SUMAS","SUNTK","SURGY","SUWEN","TABGD","TARKM","TATEN","TATGD","TAVHL","TBORG","TCELL","TCKRC","TDGYO","TEHOL","TEKTU","TERA","TEZOL","TGSAS","THYAO","TKFEN","TKNSA","TLMAN","TMPOL","TMSN","TNZTP","TOASO","TRCAS","TRGYO","TRHOL","TRILC","TSGYO","TSKB","TSPOR","TTKOM","TTRAK","TUCLK","TUKAS","TUPRS","TUREX","TURGG","TURSG","UFUK","ULAS","ULKER","ULUFA","ULUSE","ULUUN","UMPAS","UNLU","USAK","VAKBN","VAKFN","VAKKO","VANGD","VBTYZ","VERTU","VERUS","VESBE","VESTL","VKFYO","VKGYO","VKING","VRGYO","VSNMD","YAPRK","YATAS","YAYLA","YBTAS","YEOTK","YESIL","YGGYO","YGYO","YIGIT","YKBNK","YKSLN","YONGA","YUNSA","YYAPI","YYLGD","ZEDUR","ZOREN","ZRGYO",
    # Buraya geri kalan 560 sembolü ekle...
]

# Harici dosyadan okuma (semboller.txt — her satırda bir sembol):
# SEMBOLLER_DOSYASI = "semboller.txt"
# if Path(SEMBOLLER_DOSYASI).exists():
#     SEMBOLLER = [s.strip() for s in Path(SEMBOLLER_DOSYASI).read_text(encoding="utf-8").splitlines() if s.strip()]


# ─── Yardımcı fonksiyonlar ────────────────────────────────────────────────────
def url_olustur(sembol: str) -> str:
    return f"https://fintables.com/sirketler/{sembol}/sermaye-artirimlari-temettuler"


def tablo_isle(tablo_js: dict) -> list:
    headers = tablo_js.get("headers", [])
    rows    = tablo_js.get("rows", [])
    if not rows:
        return []
    max_cols = max(len(r) for r in rows)
    if not headers:
        headers = [f"Sutun {i+1}" for i in range(max_cols)]
    else:
        headers = (headers + [f"Sutun {i+1}" for i in range(len(headers), max_cols)])[:max_cols]
    rows = [r + [""] * (max_cols - len(r)) for r in rows]
    return pd.DataFrame(rows, columns=headers).to_dict(orient="records")


# ─── Tek sembol çekme ─────────────────────────────────────────────────────────
async def sembol_cek(sembol: str, page: Page, deneme: int = 0) -> dict:
    sonuc = {"sembol": sembol, "temettu": [], "sermaye_artirimi": [], "hata": None}
    try:
        # networkidle: tüm XHR/fetch istekleri tamamlanana kadar bekler
        await page.goto(url_olustur(sembol), wait_until="networkidle", timeout=SAYFA_TIMEOUT)

        # Tablo yoksa boş dön
        try:
            await page.wait_for_selector("table tbody tr", timeout=8000)
        except Exception:
            return sonuc

        # Satır sayısı stabilize olana kadar bekle (maks 4 sn)
        # "Tarihi gelmemiş" temettüler networkidle'dan 1-2 sn sonra render olabiliyor
        onceki_sayi = -1
        for _ in range(4):
            await page.wait_for_timeout(1000)
            sayi = await page.evaluate(
                "() => document.querySelectorAll('table tbody tr').length"
            )
            if sayi == onceki_sayi:
                break  # Satır sayısı değişmedi, render tamamlandı
            onceki_sayi = sayi

        tablolar = await page.evaluate("""
            () => Array.from(document.querySelectorAll('table')).map(tbl => ({
                headers: Array.from(tbl.querySelectorAll('thead th, thead td'))
                             .map(h => h.innerText.trim().replace(/\\s+/g, ' ')),
                rows: Array.from(tbl.querySelectorAll('tbody tr'))
                         .map(tr => Array.from(tr.querySelectorAll('td'))
                                       .map(td => td.innerText.trim().replace(/\\s+/g, ' ')))
                         .filter(r => r.length > 0)
            }))
        """)

        for tablo in tablolar:
            baslik = " ".join(tablo.get("headers", [])).lower()
            kayit  = tablo_isle(tablo)
            if not kayit:
                continue
            if any(k in baslik for k in ["temettu verim", "hisse basi", "brut", "dagitma",
                                          "temettü verim", "hisse başı", "brüt", "dağıtma"]):
                sonuc["temettu"] = kayit
            elif any(k in baslik for k in ["bedelsiz", "bedelli", "bolunme", "tahsisli", "sermaye",
                                            "bölünme"]):
                sonuc["sermaye_artirimi"] = kayit
            else:
                if not sonuc["temettu"]:
                    sonuc["temettu"] = kayit
                elif not sonuc["sermaye_artirimi"]:
                    sonuc["sermaye_artirimi"] = kayit

    except Exception as e:
        hata_str = str(e)
        if deneme < YENIDEN_DENEME:
            await asyncio.sleep(random.uniform(1, 2))
            return await sembol_cek(sembol, page, deneme + 1)
        sonuc["hata"] = hata_str

    return sonuc


# ─── Semaphore ile paralel çalıştırma ─────────────────────────────────────────
async def isle(sembol: str, context, semaphore: asyncio.Semaphore,
               sonuclar: list, sayac: dict, toplam: int):
    async with semaphore:
        page = await context.new_page()
        try:
            veri = await sembol_cek(sembol, page)
            sonuclar.append(veri)
            sayac["n"] += 1
            n = sayac["n"]
            if veri["hata"]:
                print(f"[{n}/{toplam}] {sembol} HATA: {veri['hata']}", flush=True)
            else:
                t = len(veri["temettu"])
                s = len(veri["sermaye_artirimi"])
                print(f"[{n}/{toplam}] {sembol}  {t} temettu | {s} sermaye artirimi", flush=True)
        finally:
            await page.close()


# ─── Ana fonksiyon ────────────────────────────────────────────────────────────
async def main():
    toplam = len(SEMBOLLER)
    print(f"\nToplam {toplam} sembol | Eszamanli tab: {CONCURRENT_TABS}\n")

    semaphore  = asyncio.Semaphore(CONCURRENT_TABS)
    sonuclar   = []
    sayac      = {"n": 0}
    baslangic  = time.time()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="tr-TR",
            extra_http_headers={
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

        gorevler = [
            asyncio.create_task(isle(s, context, semaphore, sonuclar, sayac, toplam))
            for s in SEMBOLLER
        ]
        await asyncio.gather(*gorevler)

        await context.close()
        await browser.close()

    sure = time.time() - baslangic
    hatali = [s for s in sonuclar if s.get("hata")]
    print(f"\nSure: {sure:.1f} sn ({sure/max(toplam,1):.1f} sn/sembol)")
    print(f"Basarili: {toplam - len(hatali)} | Hatali: {len(hatali)}")

    # Sonuclari sembol sirasina gore sirala
    sembol_sira = {s: i for i, s in enumerate(SEMBOLLER)}
    sonuclar.sort(key=lambda x: sembol_sira.get(x["sembol"], 9999))

    with open(CIKTI_JSON, "w", encoding="utf-8") as f:
        json.dump(sonuclar, f, ensure_ascii=False, indent=2)
    print(f"'{CIKTI_JSON}' yazildi -- {len(sonuclar)} sembol.")

    if hatali:
        with open(HATA_LOG, "w", encoding="utf-8") as f:
            json.dump({"hatali": [s["sembol"] for s in hatali]}, f, ensure_ascii=False, indent=2)
        print(f"Hatali semboller '{HATA_LOG}' dosyasina kaydedildi.")


if __name__ == "__main__":
    asyncio.run(main())
