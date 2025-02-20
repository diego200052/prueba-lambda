import json
from vehiculos import obtener_vehiculos

# Aquí se deben agregar las funciones deseadas como una tripleta.
# (Función, Path, Método HTTP)
FUNCIONES = [
    (obtener_vehiculos, 'vehiculos/obtener_vehiculos', 'GET')
]

class Funcion:
    """
        Función a ejecutar en determinada path y con determinado método
    """
    def __init__(self, func, path: str, httpMethod : str):
        self.httpMethod = httpMethod
        self.path = path
        self.func = func

    def ejecutar(self, args : dict):
        # Ejecuta la función deseada
        return self.func(**self.args)

class OrquestadorLambda:

    """
    Orquesta que funciones ejecutar acorde con el método y el path
    """

    def __init__(self):
        self.funciones : lst[Funcion] = []
        for tupla_funcion in FUNCIONES:
            # Agregamos todas las funciones que gestionará la lambda
            self.agregar_funcion(tupla_funcion[0],
                                tupla_funcion[1],
                                tupla_funcion[2])

    def agregar_funcion(self, func, path : str, httpMethod: str = 'GET'):
        if (self._verificar_path(path, httpMethod)):
            self.funciones.append(Funcion(func, path, httpMethod))
        else:
            raise Exception(f'Hay una función con un path y método repetidos: ({path} {httpMethod})')

    def _verificar_path(self, path, httpMethod):
        """
        Verifica si el path y el método ya se habían usado
        """
        for funcion in self.funciones:
            if funcion.path == path and funcion.httpMethod == httpMethod:
                return False
        return True

    
    def ejecutar_funcion(self, httpMethod : str, path : str, args : dict):
        # Busca la función dado el path y el método
        for funcion in self.funciones:
            if funcion.httpMethod == httpMethod and funcion.path == path:
                # Ejecuta la función
                funcion.ejecutar(args)


def lambda_handler(event, context):
    """
    Punto de llamada de las lambda.
    """

    # Inicializa
    try:
        orquestador_lambda = OrquestadorLambda()
    except Exception as e:
        return {
            'statusCode' : 500,
            'body': json.dumps({'error':f'Error al inicializar el orquestador lambda: {e}'})
        }

    # Obtenemos el cuerpo de la petición
    body = None
    if 'body' in event:
        body = event['body']

    #! Prueba, borrar después
    return {
        'statusCode' : 200,
        'body': json.dumps(type(body))
    }

    try:
        # Ejecutamos la función deseada
        resultado = orquestador_lambda.ejecutar_funcion(event.httpMethod)
    except:
        return {
            'statusCode': 200,
            'body': json.dumps({'error':f'Error al ejecutar la función. ( {event.httpMethod}).'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(resultado)
    }