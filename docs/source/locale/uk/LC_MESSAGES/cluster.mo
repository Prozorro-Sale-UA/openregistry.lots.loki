��          <               \      ]   �   q   }  D  �  �  4   �  P  �  �  $   API in cluster mode If during operations the server requested by cookie went down or is unavailable, client will receive :ref:`status code 412 <errors>` of request and new cookie to use. Request should be repeated with new cookie. There is a cluster of several servers that synchronize data between each other. Client should always work with the same server to ensure consistency between separate requests to the CDB. That is why cookie is required while sending POST/PUT/PATCH/DELETE requests. Cookies provide server stickiness. You can get such cookie via GET request and then use it for POST/PUT/PATCH/DELETE. Project-Id-Version: openregistry.lots.basic 0.1.dev0
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2017-08-19 13:20+0300
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: uk
Language-Team: uk <LL@li.org>
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.4.0
 Робота з API в режимі кластеру Якщо під час операцій сервер запитаний реп’яшком недоступний або впав, клієнт отримає 412 код стану запиту і новий реп’яшок. Запит потрібно повторити з використанням нового реп’яшка. Дані синхронізуються на кластері з декількох серверів. Для узгодження між окремими запитами до ЦБД важливо, щоб клієнт працював завжди з одним сервером. Тому обов’язково використовувати реп’яшок (сookie) при подачі POST/PUT/PATCH/DELETE запитів. Реп’яшки (сookies) забезпечують прив’язку до сервера. Такий реп’яшок можна отримати через GET запит, а тоді використовувати його в POST/PUT/PATCH/DELETE. 