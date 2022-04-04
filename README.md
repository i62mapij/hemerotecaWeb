# hemerotecaWeb
Trabajo Fin de Grado "Hemeroteca web para organizaciones de voluntarios"

La instalación de la aplicación requiere tener instalado un intérprete de Python versión 3.7 o superior.
Además será necesario instalar las librerías del fichero de requerimientos r.txt de la forma: \

pip install -r r.txt

Es necesario tener instalada la Base de Datos MongoDb con el usuario que se indica en la configuración de la aplicación.

Para levantar la aplicación:

python3 run.py

Es necesario tener abierto el puerto 5000 en el que escucha la aplicación.

Usuario de inicio: 

nombre: SuperadminFactory
password: SuperadminFactory

Una vez levantada la aplicación es necesario configurar los datos de la conexión con Twitter y Telegram.

Los procesos de captura se han preparado para funcionar en servidores Linux-Unix, el resto de la aplicación puede funcionar en Windows.
