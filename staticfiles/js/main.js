
// add 1 item to cart
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.add-to-cart').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
          e.preventDefault();
          const productId = this.dataset.id;

          fetch(`/cart/add-ajax/${productId}/`)
              .then(response => response.json())
              .then(data => {
                  if (data.success) {
                    // Оновлюємо лічильник
                    const cartCountEl = document.getElementById('cart-count');
                    if (cartCountEl && data.cart_count !== undefined) {
                        cartCountEl.textContent = data.cart_count;
                    }

                    // Показуємо toast
                    const toastElement = document.getElementById('cartToast');
                    const toast = new bootstrap.Toast(toastElement);
                    toast.show();
                  }
              });
      });
  });
});

