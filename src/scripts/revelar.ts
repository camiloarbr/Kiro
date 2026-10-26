// Alternativa para navegadores sin scroll-driven animations (Firefox).
// Solo corre si BaseLayout marcó <html class="io">: marca con .visible cada elemento
// animable cuando entra en pantalla y deja de observarlo.
if (document.documentElement.classList.contains('io')) {
  const observador = new IntersectionObserver(
    (entradas) => {
      for (const entrada of entradas) {
        if (!entrada.isIntersecting) continue;
        entrada.target.classList.add('visible');
        observador.unobserve(entrada.target);
      }
    },
    // -12 %: se activa cuando el elemento ya subió un poco, no apenas asoma
    { rootMargin: '0px 0px -12% 0px' },
  );

  document.querySelectorAll('.revela, .revela-2, [data-io]').forEach((el) => observador.observe(el));
}
