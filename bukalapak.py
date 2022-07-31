# Bukalapak Product Scrapper v1.0
# heryandp

from bs4 import BeautifulSoup as bs
import requests as req
import glob, json, os,csv,time

# baseurl
baseurl = 'https://www.bukalapak.com/u/'
apiurl = 'https://api.bukalapak.com/stores/'

class bukalapak():
    def __init__(self,username):
        self.username = username
        self.urltoko = baseurl+username
        self.headerbrowser = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'}
        pg_data = req.get(self.urltoko, headers=self.headerbrowser, timeout=3000)
        try:
            if pg_data.status_code == 200:
                soup = bs(pg_data.text, 'html.parser')
                # grabbing seller id
                print("[+] Mengambil id penjual ...")
                self.idseller = soup.find('a',attrs={'data-user-id':True}).get('data-user-id')
                print("[+] Id penjual : "+self.idseller)
                # grabbing access token for api
                print("[+] Mengambil access token ...")
                stoken = soup.find_all('script')
                gtoken = str(stoken[4]).replace("<script>localStorage.setItem('bl_token', '","").replace("');</script>","")
                gtoken = json.loads(str(gtoken))
                self.token = gtoken['access_token']
                print("[+] Access token : "+self.token)
                self.grabproduk()
            else:
                print("[!] Username tidak ditemukan!")
        except Exception as e:
            print(e)
            print("[!] Website down!")
            exit()   
    def grabproduk(self):
        print("=== GRABBING PRODUK ===")
        print("[+] Memulai download halaman produk ...")
        print("\x1B[3m" +"(delay 3 detik untuk menghindari anti-spam!)"+"\x1B[0m")
        api = apiurl+str(self.idseller)+'/products?offset=0&limit=50&access_token='+self.token
        total_product = req.get(api, headers=self.headerbrowser, timeout=3000).json()
        print("[+] Total produk : "+str(total_product['meta']['total']))
        print("[+] Hapus file lama ...")
        if not os.path.exists("data"):
            os.makedirs("data")
        for filename in glob.glob("data/"+str(self.idseller)+"_bukalapak*.json"):
            os.remove(filename)
        for filename in glob.glob(str(self.idseller)+"_bukalapak.csv"):
            os.remove(filename)
        # grabbing halaman produk
        a = 0
        b = 0
        while(True):
            print("-> download halaman ke-"+str(b+1))
            api = apiurl+str(self.idseller)+'/products?offset='+str(a)+'&limit=50&access_token='+self.token
            pg_data = req.get(api, headers=self.headerbrowser, timeout=3000).json()
            if len(pg_data['data']) == 0:
                break
            with open("data/"+str(self.idseller)+"_bukalapak_"+str(b)+'.json', 'w') as json_file:
                    json.dump(pg_data['data'], json_file)
            a += 50
            b += 1
            time.sleep(3)
        # merging json
        print("[+] Merging data produk ...")
        data = []
        for f in glob.glob("data/"+str(self.idseller)+"_bukalapak*.json"):
            with open(f,) as infile:
                data.extend(json.load(infile))
        with open("data/"+str(self.idseller)+"_bukalapak_all.json",'w') as outfile:
            json.dump(data, outfile)
        # create csv
        print("[+] Membuat csv data produk ...")
        f_data = []
        f = open("data/"+str(self.idseller)+"_bukalapak_all.json")
        f_read = json.load(f)
        for i in f_read:
            f_data.append([
                self.idseller,
                self.username,
                i['store']['name'],
                i['store']['level']['name'],
                i['store']['premium_level'],
                i['id'],
                i['name'],
                i['category']['name'],
                i['condition'],
                i['rating']['average_rate'],
                i['rating']['user_count'],
                i['stock'],
                i['stats']['interest_count'],
                i['stats']['sold_count'],
                i['stats']['view_count'],
                i['price'],
                i['original_price'],
                i['discount_percentage'],
                i['description']
            ])
        f_header = ['id_seller','username','nama_toko','level_toko','premium_toko','id_produk','nama_produk','kategori','kondisi','rating','jumlah_rating','stok','jumlah_interest','jumlah_sold','jumlah_view','harga','harga_asli','diskon','deskripsi']
        with open(str(self.idseller)+'_bukalapak.csv', 'w',newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(f_header)
            writer.writerows(f_data)
        print('done! '+str(self.idseller)+'_bukalapak.csv')
        f.close()

print("[ BUKALAPAK-PRODUCT-GRABBER v1.0 by heryan ]")
print("______       _         _                   _    ")
print("| ___ \     | |       | |                 | |   ")
print("| |_/ /_   _| | ____ _| | __ _ _ __   __ _| | __")
print("| ___ \ | | | |/ / _` | |/ _` | '_ \ / _` | |/ /")
print("| |_/ / |_| |   < (_| | | (_| | |_) | (_| |   < ")
print("\____/ \__,_|_|\_\__,_|_|\__,_| .__/ \__,_|_|\_>")
print("                              | |               ")
print("                              |_|               ")
print("[+] https://github.com/heryandp/bukalapak-product-scrap")
sname = input("[+] Masukkan username seller: https://www.bukalapak.com/u/")        
act = bukalapak(sname)