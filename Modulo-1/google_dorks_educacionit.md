# Google Dorks — 20 ejemplos con educacionit.com

Reconocimiento 100% pasivo: son búsquedas en Google, no tocan el servidor de `educacionit.com` en ningún momento. Se usa este dominio porque ya tenemos autorización del instituto para reconocimiento pasivo (ver `comandos_clase_1.md`).

Probados en vivo antes de la clase — algunos traen resultados reales, otros no (y eso también es una lección: ausencia de resultados es buena higiene, no un fallo del dork).

---

## A. Subdominios y entornos

1. `site:educacionit.com -site:www.educacionit.com`
   Todo lo indexado fuera del sitio principal — la forma más rápida de listar subdominios sin herramientas.

2. `site:dev.educacionit.com`
   Contenido indexado del entorno de desarrollo. Los entornos `dev`/`test` suelen tener menos hardening que producción.

3. `site:test.educacionit.com OR site:testealo.educacionit.com`
   Entornos de testing. `testealo.educacionit.com` apareció como resultado real al buscar `intitle:"index of"` — vale la pena mostrarlo en vivo.

4. `site:intranet.educacionit.com`
   Si el intranet corporativo tiene algo indexado, es información que no debería ser pública.

---

## B. Archivos expuestos

5. `site:educacionit.com filetype:pdf`
   Confirmado con resultados reales: temarios de cursos (`/pdf/temarios/...`). Buen ejemplo de exposición **intencional** vs. accidental — discutir la diferencia con la clase.

6. `site:educacionit.com filetype:xlsx OR filetype:csv`
   Planillas que pudieron subirse sin querer (listados de alumnos, notas, contactos).

7. `site:educacionit.com filetype:sql`
   Dumps de base de datos expuestos — el hallazgo más grave de esta categoría.

8. `site:educacionit.com filetype:env OR filetype:log`
   Archivos de configuración o logs de aplicación que no deberían ser servidos por el webserver.

9. `site:educacionit.com filetype:bak OR filetype:old OR filetype:backup`
   Backups olvidados — clásico de despliegues manuales.

---

## C. Paneles de administración y login

10. `site:educacionit.com inurl:login`
    Confirmado con resultados reales: `login.educacionit.com` y `empresas.educacionit.com/Identity/Account/Login`. Ya mapea 2 superficies de autenticación distintas.

11. `site:educacionit.com inurl:admin OR inurl:panel`
    Paneles administrativos — superficie de ataque de alto valor si no tienen MFA.

12. `site:empresas.educacionit.com inurl:Identity`
    El login de `empresas` usa ASP.NET Identity (visto en el resultado real) — dispara la pregunta: ¿qué versión? ¿vulnerabilidades conocidas?

---

## D. Información técnica / stack

13. `site:educacionit.com inurl:api`
    Endpoints de API públicos — insumo directo para la fase de enumeración de la próxima clase.

14. `site:educacionit.com intitle:"swagger" OR inurl:swagger`
    Documentación de API expuesta — si aparece, es un mapa completo del backend regalado.

15. `site:educacionit.com inurl:wp-admin OR inurl:wp-content`
    Si algún subdominio corre WordPress, esto lo confirma sin necesidad de whatweb.

---

## E. Higiene del sitio / errores

16. `site:educacionit.com intitle:"index of"`
    Directory listing habilitado. Probado en vivo: **sin resultados** — buena señal de higiene, mostrarlo igual sirve para explicar qué pasaría si SÍ apareciera.

17. `site:educacionit.com intext:"error" intext:"stack trace"`
    Errores verbosos que filtran rutas internas, versiones de librerías o queries SQL.

18. `site:educacionit.com intext:"Warning:" OR intext:"Notice:"`
    Errores de PHP no silenciados — típico en entornos con `display_errors` mal configurado.

---

## F. Credenciales y menciones externas

19. `site:educacionit.com intext:"password" OR intext:"contraseña"`
    Páginas que mencionan credenciales en el texto (documentación mal ubicada, formularios de soporte, etc.).

20. `site:pastebin.com "educacionit.com"`
    Menciones del dominio en pastebins — leaks de terceros (empleados, ex-alumnos) que no dependen de una falla propia del sitio, pero siguen siendo parte del reconocimiento pasivo.

---

## Notas para la clase

- Todos estos dorks corren en la barra de búsqueda de Google — cero interacción con `educacionit.com`.
- Si un dork no trae nada (como el #16), es una buena oportunidad para preguntar: *"¿por qué no aparece? ¿qué tendrían que hacer mal para que sí apareciera?"*
- Los hallazgos de A/C ya dan pie a preguntas de la próxima clase (enumeración, superficie de auth) — se puede usar como gancho de cierre.
