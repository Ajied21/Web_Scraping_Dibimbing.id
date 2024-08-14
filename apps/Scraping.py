import requests
import pandas as pd

# URL target dan header
url_target = 'https://gql.tokopedia.com/graphql/SearchProductQueryV4'

header = {
    'authority': 'gql.tokopedia.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.tokopedia.com',
    'referer': 'https://www.tokopedia.com/search?fcity=144%2C146%2C150%2C151%2C167%2C168%2C171%2C174%2C175%2C176%2C177%2C178%2C179%2C463&navsource=&search_id=20240729055520182264294B240D197BRI&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&q=laptop%20gaming',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'tkpd-userid': '0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/108.0.0.0 Safari/537.36',
    'x-device': 'desktop-0.0',
    'x-source': 'tokopedia-lite',
    'x-tkpd-lite-service': 'zeus',
    'x-version': '68ba647'
}

# Daftar nama merek
brands = ['ASUS', 'ACER', 'ADVAN', 'ALIENWARE', 'APPLE', 'AXIOO', 'DELL', 'EPSON', 'HP', 'HUAWEI', 'INFINIX', 
        'LENOVO', 'MSI', 'MEYFAH', 'MICROSOFT', 'PANASONIC', 'RAZER', 'REALME', 'ROYCO', 'SAMSUNG', 'TOSHIBA', 
        'VIVO', 'XIAOMI', 'ZYREX', 'asus', 'acer', 'advan', 'alienware', 'apple', 'axioo', 'dell', 'epson', 'hp', 
        'huawei', 'infinix', 'lenovo', 'msi', 'meyfah', 'microsoft', 'panasonic', 'razer', 'realme', 'royco', 'samsung', 
        'toshiba', 'vivo', 'xiaomi', 'zyrex', 'Asus', 'Acer', 'Advan', 'Alienware', 'Apple', 'Axioo', 'Dell', 'Epson', 'Hp', 
        'Huawei', 'Infinix', 'Lenovo', 'Msi', 'Meyfah', 'Microsoft', 'Panasonic', 'Razer', 'Realme', 'Royco', 'Samsung', 'Toshiba', 
        'Vivo', 'Xiaomi', 'Zyrex']

# Fungsi untuk mengekstrak nama merek dari kolom 'name'
def extract_brand(name):
    for brand in brands:
        if brand in name:
            return brand.lower()  # Mengembalikan nama merek dalam huruf kecil
    return None

# Inisialisasi variabel
all_products = []
page = 1

while True:
    # Menyusun GraphQL query
    query = f'[{{"operationName":"SearchProductQueryV4","variables":{{"params":"device=desktop&navsource=&ob=23&page={page}&q=laptop%20gaming&related=true&rows=60&safe_search=false&scheme=https&shipping=&source=search&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&user_addressId=&user_cityId=&user_districtId=&user_id=&user_lat=&user_long=&user_postCode=&user_warehouseId=&variants="}}, "query":"query SearchProductQueryV4($params: String!) {{ ace_search_product_v4(params: $params) {{ data {{ products {{ id name price imageUrl rating countReview url shop {{ city isOfficial isPowerBadge name }} }} }} }} }}"}}]'

    # Mengirim permintaan POST ke endpoint
    response = requests.post(url_target, headers=header, data=query)

    # Mengambil data produk dari respons JSON
    response_data = response.json()
    products = response_data[0]['data']['ace_search_product_v4']['data']['products']

    if not products:
        # Jika tidak ada produk, hentikan iterasi
        break

    # Menambahkan produk ke list
    all_products.extend(products)

    # Pindah ke halaman berikutnya
    page += 1

# Membuat DataFrame pandas dari semua produk
df = pd.DataFrame(all_products)

# Menghapus prefix 'Rp' dari kolom 'price' dan mengubahnya menjadi tipe float
df['price'] = df['price'].str.replace('Rp', '').str.replace('.', '').astype(float)

# Memisahkan kolom 'shop' menjadi kolom terpisah
df['location'] = df['shop'].apply(lambda x: x['city'])
df['status_Official'] = df['shop'].apply(lambda x: x['isOfficial'])
df['power_badge'] = df['shop'].apply(lambda x: x['isPowerBadge'])
df['shop_name'] = df['shop'].apply(lambda x: x.get('name'))

# Menghapus kolom 'shop' yang sudah tidak diperlukan
df = df.drop(columns=['shop'])

# Menambahkan kolom 'Brand' berdasarkan nama merek
df['brand'] = df['name'].apply(extract_brand)

#mengganti nama kolom
df = df.rename(columns={"countReview": "count_review"})
df = df.rename(columns={"url": "URL"})

if __name__ == "__main__":

    try:
        #ambil data yang diperlukan
        data_fixed = df[["id", "name", "brand", "price", "rating", "count_review",
                        "status_Official", "power_badge", "location", "shop_name", "URL"]]
        
        # Mengonversi tipe data kolom-kolom yang diperlukan
        data_fixed["name"]  = data_fixed["name"].astype(str)
        data_fixed["brand"] = data_fixed["brand"].astype(str)
        data_fixed["price"] = data_fixed["price"].astype(int)
        data_fixed["rating"] = data_fixed["rating"].astype(float)
        data_fixed["count_review"] = data_fixed["count_review"].astype(int)
        data_fixed["status_Official"] = data_fixed["status_Official"].astype(bool)
        data_fixed["power_badge"] = data_fixed["power_badge"].astype(bool)
        data_fixed["location"] = data_fixed["location"].astype(str)
        data_fixed["shop_name"] = data_fixed["shop_name"].astype(str)
        data_fixed["URL"] = data_fixed["URL"].astype(str)

        # Menampilkan DataFrame
        print(data_fixed)

        data_fixed.to_csv('./Data/Tokopedia_Laptop_Gaming.csv', index=False)

        print(f"Scraping website Tokopedia to success...")

    except Exception as e:
        print(f"Terjadi kesalahan : {e}")