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

$(".hesap").ready(function() {
    $('#sifreDegistir').click(function() {
        // Yeni şifre alanlarını görünür yap
        $('.new-password-fields').show();
        
        // Yeni şifre alanlarını al
        var new_password = $('#new_password').val();
        var confirm_password = $('#confirm_password').val();
        
       
        // Yeni şifreler uyuşmuyorsa hata ver
        if (new_password !== confirm_password) {
            alert("Yeni şifreler uyuşmuyor. Lütfen tekrar deneyin.");
            // Uyuşmadıkları için işlemi durdur
            return;
        }

		 // Yeni şifre alanlarının dolu olup olmadığını kontrol et
		 if (new_password === '' || confirm_password === '') {
            alert("Lütfen yeni şifre alanlarını doldurun.");
            // Dolu olmadıkları için işlemi durdur
            return;
        }


        // AJAX ile şifre değiştirme işlemini gerçekleştir
        $.ajax({
            url: '/change-password',
            method: 'POST',
            data: { new_password: new_password },
            success: function(response) {
                alert(response.message);
                // Şifre değiştirme başarılı olduğunda hesabim.html sayfasına yönlendir
               
                $('#sifre').val(new_password);
				$('#new_password').val('');
                $('#confirm_password').val('');
				
            },
            error: function(xhr, status, error) {
                alert("Şifre değiştirme sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.");
            }
        });
    });
});


$(document).ready(function() {
    function getData() {
        $.ajax({
            type: 'GET',
            url: '/get_data',
            success: function(response) {
                console.log(response);
                var formContent = $('#formContent');
                var table = $('<div class="table-responsive"></div>');
                var tableInner = '<table class="table table-bordered">';
                var tableHeader = '<thead><tr><th></th>'; // Boş başlık sütunu eklendi
                
                // Tablo başlıklarını oluştur
                $.each(response[0], function(key, value) {
                    tableHeader += '<th>' + key + '</th>';
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
                
                // Form içine tabloyu ekle
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
                    traditional: true, // PHP tarafında dizi olarak almak için gerekli
                    success: function(response) {
                        // Sözleşmeler başarıyla silindiğinde, tablodan kaldır
                        $.each(selectedContractIds, function(index, contractId) {
                            $('#formContent input[value="' + contractId + '"]').closest('tr').remove();
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
});
