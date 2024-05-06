import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

def check_updates():
    url = "https://bugzilla.mozilla.org/buglist.cgi?quicksearch=webgl&list_id=17021492"

    # Web sayfasından veriyi çek
    response = requests.get(url)

    # İsteğin başarılı olup olmadığını kontrol et
    if response.status_code == 200:
        # BeautifulSoup kütüphanesiyle sayfanın kaynak kodunu işle
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Tüm <tr> etiketlerini bulun
        tr_tags = soup.find_all('tr', class_='bz_bugitem')
        
        # Her bir <tr> etiketini döngüye alın
        for tr_tag in tr_tags:
            # Her bir etiketten gerekli verileri çekin
            bug_id = tr_tag.find('td', class_='bz_id_column').text.strip()
            summary = tr_tag.find('td', class_='bz_short_desc_column').text.strip()
            summary_href = tr_tag.find('td', class_='bz_short_desc_column').a['href']
            status = tr_tag.find('td', class_='bz_bug_status_column').text.strip()
            
            # Çekilen verileri yazdırın
            print('ID:', bug_id)
            print('Summary:', summary)
            print('SummaryHref:', 'https://bugzilla.mozilla.org/show_bug.cgi?id={}'.format(summary_href))
            print('Status:', status)
            print('---')
    else:
        print("Sayfa yüklenirken bir hata oluştu. Durum kodu:", response.status_code)

# Zamanlayıcı oluştur
scheduler = BlockingScheduler()

# Belirli aralıklarla check_updates fonksiyonunu çalıştır
scheduler.add_job(check_updates, 'interval', seconds=10)

# Zamanlayıcıyı başlat
scheduler.start()
