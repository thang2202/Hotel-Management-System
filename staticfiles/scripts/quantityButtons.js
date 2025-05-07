function qtySum() {
    // Lấy tất cả các input có tên 'adult' và 'children'
    var adultInput = document.querySelector("input[name='adult']");
    var childrenInput = document.querySelector("input[name='children']");

    // Tính tổng số khách
    var totalGuests = parseInt(adultInput.value || 0) + parseInt(childrenInput.value || 0);

    // Cập nhật tổng số khách
    var qtyTotal = document.querySelector(".qtyTotal");
    qtyTotal.innerHTML = totalGuests;
}
qtySum();
$(function() {
    $(".qtyButtons input").after('<div class="qtyInc"></div>');
    $(".qtyButtons input").before('<div class="qtyDec"></div>');
    $(".qtyDec, .qtyInc").on("click", function() {
        var $button = $(this);
        var oldValue = $button.parent().find("input").val();
        if ($button.hasClass('qtyInc')) {
            var newVal = parseInt(oldValue) + 1;
        } else {
            if (oldValue > 0) {
                var newVal = parseInt(oldValue) - 1;
            } else {
                newVal = 0;
            }
        }
        $button.parent().find("input").val(newVal);
        qtySum();
        $(".qtyTotal").addClass("rotate-x");
    });

    function removeAnimation() {
        $(".qtyTotal").removeClass("rotate-x");
    }
    const counter = document.querySelector(".qtyTotal");
    counter.addEventListener("animationend", removeAnimation);
});
$(window).on('load resize', function() {
    var panelTrigger = $('.booking-widget .panel-dropdown a');
    $('.booking-widget .panel-dropdown .panel-dropdown-content').css({
        'width': panelTrigger.outerWidth()
    });
});