# Flask_Splunk_Project
Python Flask kütüphanesi ile iki script'in web arayüzü üzerinden çalıştırılması ve sonuç alınması sağlandı. Script'lerde api ile Splunk'a sorgu yapılmaktadır.

SplunkLogCheck sayfasında sunucuların metricslog ve wineventlog'larının gelip gelmediğini .xlsx uzantılı dosyada ayrı sheetlerde gösterilmesi sağlanmıştır.
Teftis sayfasında sorgu atmak istediğiniz tarihleri gün bazında seçebilirsiniz. Çoklu gün seçimleri için Splunk'da her gün için multithread ile eşzamanlı olarak sorgu atıp sonucu ziplenmiş dosya olarak ve içinde .xlsx uzantılı dosyalar olarak dönmesi sağlanmıştır. Banka müfettişleri tarafından istenen logları kısa bir şekilde hazırlamak için hazırlanmıştır.
