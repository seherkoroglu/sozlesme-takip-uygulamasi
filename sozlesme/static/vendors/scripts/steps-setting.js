
// Formdaki tüm alanları kontrol eden bir işlev
function validateForm() {
    var isValid = true;
    $('.tab-wizard section:visible input, .tab-wizard section:visible select, .tab-wizard section:visible textarea').each(function() {
        if ($(this).val() === '') {
            isValid = false;
            return false; // Döngüyü sonlandır
        }
    });
    return isValid;
}

// jQuery Steps eklentisini başlat
$(".tab-wizard").steps({
    headerTag: "h5",
    bodyTag: "section",
    transitionEffect: "fade",
    titleTemplate: '<span class="step">#index#</span> #title#',
    labels: {
        finish: "Ekle",
        next: "İleri",
        previous: "Geri",
    },
    onStepChanged: function (event, currentIndex, priorIndex) {
        $('.steps .current').prevAll().addClass('disabled');
    },
    onStepChanging: function (event, currentIndex, newIndex) {
        // Yeni adıma geçmeden önce doğrulama yap
        if (newIndex > currentIndex) {
            return validateForm(); // Doğrulama sonucunu döndür
        }
        return true; // Yeni adıma geç
    },

	onFinished: function (event, currentIndex) {
		$('#success-modal').modal('show');
		onclick = addSozlesme(event);
        
	}
});
$(".tab-wizard2").steps({
	headerTag: "h5",
	bodyTag: "section",
	transitionEffect: "fade",
	titleTemplate: '<span class="step">#index#</span> <span class="info">#title#</span>',
	labels: {
		finish: "Ekle",
		next: "İleri",
		previous: "Geri",
	},
	onStepChanged: function(event, currentIndex, priorIndex) {
		$('.steps .current').prevAll().addClass('disabled');
	},
	onFinished: function(event, currentIndex) {
		$('#success-modal-btn').trigger('click');
		onclick=addSozlesme(event);
	}
});


$(".hesap").steps({
    headerTag: "h5",
    bodyTag: "section",
    titleTemplate: '<span class="step">#index#</span> #title#',
    labels: {
        finish: "Hesabı Sil",
        current: ""
    },
    onFinished: function (event, currentIndex) {
		hesabiSil(event);
    }
});

// Hesabı Sil butonuna tıklandığında yapılacak işlem
function hesabiSil(event) {
    // Kullanıcıyı uyar
    var confirmDelete = confirm("Hesabınızı silmek istediğinizden emin misiniz?");
    
    // Eğer kullanıcı işlemi onaylarsa
    if (confirmDelete) {
        // AJAX isteği göndererek hesabı silme işlemini gerçekleştir
        $.ajax({
            type: "POST",
            url: "/delete-account", // Flask route'u
            success: function(response) {
                // İşlem başarılıysa kullanıcıya bilgi ver
                alert(response.message);
                // Oturumu sonlandır ve ana sayfaya yönlendir
                window.location.href = "/";
            },
            error: function(error) {
                // Hata durumunda kullanıcıya bilgi ver
                alert("Hesabı silme işleminde bir hata oluştu.");
            }
        });
    }
}



    



$(document).ready(function() {
    var columnMappings = {
        "sozlesme_id": "Sözleşme Numarası",
        "aciklama": "Açıklama",
        "baslangic_tarihi": "Başlangıç Tarihi",
        "bitis_tarihi": "Bitiş Tarihi",
        "bilgilendirme_amaci": "Bilgilendirme Amacı",
        "bilgilendirme_saati": "Bilgilendirme Saati",
        "bilgilendirme_tarihi": "Bilgilendirme Tarihi",
        "bilgilendirme_tipi": "Bilgilendirme Tipi",
        "departman_adi": "Departman Adı",
        "firma_adi": "Firma Adı",
        "ilgili_firma_adi": "İlgili Firma Adı",
        "imza_yetkilisi": "İmza Yetkilisi",
        "kullanici_id": "Kullanıcı Numarası",
        "sozlesme_basligi": "Sözleşme Başlığı",
        "sozlesme_icerigi": "Sözleşme İçeriği",
        "sozlesme_kodu": "Sözleşme Kodu",
    };

    function getData() {
        $.ajax({
            type: 'GET',
            url: '/get_data',
            success: function(response) {
                console.log(response);
                var formContent = $('#formContent');
                var table = $('<div class="table-responsive"></div>');
                var tableInner = '<table class="table table-bordered">';
                var tableHeader = '<thead><tr><th></th>'; // Boş başlık sütunu ekle
                
                // Tablo başlıklarını oluştur
                $.each(response[0], function(key, value) {
                    var columnHeader = columnMappings[key] || key; // Eğer sütun adı varsa onun karşılık geldiği başlığı kullan, yoksa sütun adını kullan
                    tableHeader += '<th>' + columnHeader + '</th>';
                });
                tableHeader += '</tr></thead>';
                tableInner += tableHeader;
                
                // Verileri tabloya ekle
                $.each(response, function(index, contract) {
                    var row = '<tr>';
                    row += '<td><input type="checkbox" class="contractCheckbox" value="' + contract.sozlesme_id + '"></td>'; // Checkbox ekle
                    $.each(contract, function(key, value) {
                        row += '<td>' + value + '</td>';
                    });
                    row += '</tr>';
                    tableInner += row;
                });
                
                tableInner += '</table>';
                table.append(tableInner);
                
                // Form içine tabloyu ekleme kodu
                formContent.append(table);
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    }


    // Verileri al
    getData();

    // Sözleşme silme işlemi
    $('#deleteButton').on('click', function() {
        var selectedContractIds = $('.contractCheckbox:checked').map(function() {
            return $(this).val();
        }).get();
        
        if (selectedContractIds.length > 0) {
            if (confirm('Seçilen sözleşmeleri silmek istediğinizden emin misiniz?')) {
                $.ajax({
                    type: 'POST',
                    url: '/delete_contract',
                    data: { sozlesme_ids: selectedContractIds },
                    traditional: true, // PHP tarafında dizi olarak almak için 
                    success: function(response) {
                        // Sözleşmeler başarıyla silindiğinde, tablodan kaldırma kodu
                        $.each(selectedContractIds, function(index, contract_id) {
                            $('#formContent input[value="' + contract_id + '"]').closest('tr').remove();
                        });
                        alert('Sözleşmeler başarıyla silindi.');
                    },
                    error: function(xhr, status, error) {
                        console.error(xhr.responseText);
                        alert('Sözleşmeler silinirken bir hata oluştu.');
                    }
                });
            }
        } else {
            alert('Lütfen silmek istediğiniz sözleşmeleri seçin.');
        }
    });

    // PDF oluşturma fonksiyonu
function createPDF(data) {
    var contracts = data.map(function(contract) {
        var contractInfo = [
            'Sözleşme ID: ' + contract.sozlesme_id,
            'Firma Adı: ' + contract.firma_adi,
            'Departman: ' + contract.departman_adi,
            'Başlangıç Tarihi: ' + contract.baslangic_tarihi,
            'Bitiş Tarihi: ' + contract.bitis_tarihi,
            'Sözleşme Kodu: ' + contract.sozlesme_kodu,
            'Sözleşme Başlığı: ' + contract.sozlesme_basligi,
            'Sözleşme İçeriği: ' + contract.sozlesme_icerigi,
            'İmza Yetkilisi: ' + contract.imza_yetkilisi,
            'İlgili Firma: ' + contract.ilgili_firma_adi,
            'Bilgilendirme Tipi: ' + contract.bilgilendirme_tipi,
            'Bilgilendirme Tarihi: ' + contract.bilgilendirme_tarihi,
            'Bilgilendirme Saati: ' + contract.bilgilendirme_saati,
            'Bilgilendirme Amacı: ' + contract.bilgilendirme_amaci,

            
        ];
        return contractInfo.join('<br>');
    }).join('<br><br>');

    var element = document.createElement('div');
    element.innerHTML = contracts;

    html2pdf()
        .from(element)
        .save('contracts.pdf');
}


$('#pdfbutton').on('click', function() {
    $.ajax({
        type: 'GET',
        url: '/get_data',
        success: function(response) {
            createPDF(response);
        },
        error: function(xhr, status, error) {
            console.error(xhr.responseText);
            alert('Veri alınırken bir hata oluştu.');
        }
    });
});



});




