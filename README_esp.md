## Prototipo de Tutorial Maker 

### Instalación

- Instale la [última versión estable de 3D Slicer](https://download.slicer.org) (actualmente 3D Slicer-5.6.2)
- Abra el repositorio [Tutorial Maker](https://github.com/SlicerLatinAmerica/TutorialMaker) en GitHub
- Clone el botón verde “Code” y seleccione la opción “Download ZIP” como se muestra en la imagen de abajo para descargar el archivo “TutorialMaker.zip” en su computadora
![image](DOCS/Img_es/DescargarRepo.png)
- Descomprima el archivo “TutorialMaker.zip” para acceder al directorio “TutorialMaker-main”

- **Para usuarios de Windows**: 
    1. Inicie 3D Slicer
    2. Arrastre y suelte la carpeta “TutorialMaker” en la ventana de la aplicación de Slicer. 
    3. Aparecerá una primera ventana emergente, “Seleccionar un lector”. Seleccione “Añadir módulos de scripting Python a la aplicación” y haga clic en OK.
    4. Aparece una segunda ventana emergente para cargar el módulo Tutorial Maker. Haga clic en “Sí”.
    ![image](DOCS/Img_es/InstalarWindows.gif)

- **Para usuarios de MacOs**: 
    1. Inicie 3D Slicer.
    2. Seleccione “Editar” en el menú principal
    3. Seleccione “Parámetros de la aplicación”
    4. Aparecerá una ventana de “Parámetro”': seleccione “Módulos” en el panel izquierdo
    5. Seleccione el archivo 'TutoriaMaker.py'.
    6. Arrastre y suelte el archivo TutorialMaker.py situado en el subdirectorio TutorialMaker-main/TutorialMaker/'en el campo “Rutas de módulos adicionales” y haga clic en OK para reiniciar Slicer
    ![image](DOCS/Img_es/InstalarMac.gif)

### Cómo utilizar Tutorial Maker

- Seleccione el módulo “Tutorial Maker” en la categoría “Utilidades” de la lista de módulos de Slicer. 
![image](DOCS/Img_es/SeleccionarModulo.png)
> [!ADVERTENCIA]
> Antes de empezar este tutorial, cambie Slicer al modo de pantalla completa y ajuste el tamaño de la fuente a 14pt para asegurarse de que las capturas de pantalla son fáciles de leer.

- Seleccione `fourMin_tutorial`
![image](DOCS/Img_es/Seleccionar4min.png)

- Dé click en `Ejecutar y anotar`
![image](DOCS/Img_es/SeleccionarEjecutar.png)

### Herramienta de anotaciones

-	Las capturas de pantalla aparecerán a la izquierda.
![image](DOCS/Img_es/Miniaturas.png)
-	Cada captura de pantalla tiene un título(flecha verde) y un comentario(flecha roja).
![image](DOCS/Img_es/TituloDescripcion.png)
- Seleccione una de las tres herramientas de anotación.
![image](DOCS/Img_es/Anotaciones.png)
-	Tras seleccionar una herramienta, especifique el estilo y el texto de la anotación.
![image](DOCS/Img_es/Flechas.png)
-	A continuación, haga clic en el elemento que recibirá la anotación.
![image](DOCS/Img_es/Anotaciones.gif)

> [!ADVERTENCIA]
> Para las personas que padecen epilepsia, la pantalla parpadeará en cada captura.
- Después de crear todas las anotaciones, haga clic en “Guardar archivo”.
![image](DOCS/Img_es/PDF.png)

- Las capturas de pantalla con anotaciones se guardarán ahora en la carpeta del Módulo en “Salidas”;
![image](https://github.com/SlicerLatinAmerica/TutorialMaker/assets/28208639/3a5feeb0-b7a3-41c8-923f-77239f5331c8)

### Escribir tutoriales

TODO: Crear el "manual del desarrollador" para crear nuevos tutoriales.
