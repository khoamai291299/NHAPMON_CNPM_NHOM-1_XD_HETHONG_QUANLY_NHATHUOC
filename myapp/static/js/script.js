/*------------------------------------------------------------------
* Bootstrap Simple Admin Template
* Version: 2.1
* Author: Alexis Luna
* Website: https://github.com/alexis-luna/bootstrap-simple-admin-template
-------------------------------------------------------------------*/
// Toggle sidebar on Menu button click
$('#sidebarCollapse').on('click', function() {
    $('#sidebar').toggleClass('active');
    $('#body').toggleClass('active');
});

// Auto-hide sidebar on window resize if window size is small
// $(window).on('resize', function () {
//     if ($(window).width() <= 768) {
//         $('#sidebar, #body').addClass('active');
//     }
// });

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    if (user && pass) {
        console.log("Login attempt:", user);
        alert("Đang xác thực thông tin...");
    } else {
        alert("Vui lòng điền đầy đủ Username và Password!");
    }
});