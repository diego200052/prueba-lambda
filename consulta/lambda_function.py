import json
import traceback
import inspect
import urllib.parse
from vehiculos import obtener_vehiculos

# Aquí se deben agregar las funciones deseadas como una tripleta.
# (Función, Path, Método HTTP)
FUNCIONES = [
    (obtener_vehiculos, '/vehiculos/obtener-vehiculos', 'GET')
]

class Funcion:
    """
        Función a ejecutar en determinada path y con determinado método
    """
    def __init__(self, func, path: str, http_method: str):
        self.path = path
        self.http_method = http_method
        self.func = func

    def ejecutar(self, args : dict):
        # Filtramos los args que la función necesita
        signature = inspect.signature(self.func)

        # Obtener los nombres de los parámetros necesarios (incluye parámetros posicionales y con valor por defecto)
        required_params = {param.name for param in signature.parameters.values()}

        # Filtrar el diccionario de argumentos, dejando solo los necesarios
        filtered_args = {key: value for key, value in args.items() if key in required_params}

        # Ejecuta la función deseada
        return self.func(**filtered_args)
    
    def get_params(self):
        signature = inspect.signature(self.func)
        params = {
            'error' : 'No se introdujeron los parámetros necesarios para devolver una respuesta.',
            'params': [
                {
                    'name': param.name,
                    'type': 'Obligatorio' if param.default == inspect.Parameter.empty else 'Opcional'
                }
                for param in signature.parameters.values()
            ]
        }
        return params

class OrquestadorLambda:

    """
    Orquesta que funciones ejecutar acorde con el método y el path
    """

    def __init__(self):
        self.funciones : list[Funcion] = []
        for tupla_funcion in FUNCIONES:
            # Agregamos todas las funciones que gestionará la lambda
            self.agregar_funcion(tupla_funcion[0],
                                tupla_funcion[1],
                                tupla_funcion[2])

    def agregar_funcion(self, func, path : str, http_method : str):
        if (self._verificar_path_method(path, http_method)):
            self.funciones.append(Funcion(func, path, http_method))
        else:
            raise Exception(f'Hay una función con un path y método repetidos: ({path} {http_method})')

    def _verificar_path_method(self, path, http_method):
        """
        Verifica si el path y el método ya se habían usado
        """
        for funcion in self.funciones:
            if funcion.path == path and funcion.http_method == http_method:
                return False
        return True

    def _convertir_body_a_dict(self, http_method, body):
        if (type(body) == dict):
            return body
        if (type(body) == str and http_method == 'GET'):
            return {key: value[0] for key, value in urllib.parse.parse_qs(body).items()}
        return {}
    
    def ejecutar_funcion(self, path : str, http_method : str, body, content_type : str):
        # Busca la función dado el path y el método
        for funcion in self.funciones:
            if funcion.path == path and funcion.http_method == http_method:
                # Ejecuta la función
                args = self._convertir_body_a_dict(http_method, body, content_type)
                try:
                    return funcion.ejecutar(args)
                except Exception as e:
                    if 'unexpected keyword argument' in str(e):
                        return funcion.get_params()
                    else:
                        raise

        raise Exception('El path de la función no existe o el método http es incorrecto.')


def json_response(httpStatusCode : int = 500, body : dict = {}):
    return {
        # "isBase64Encoded": isBase64Encoded,
        "statusCode": httpStatusCode,
        # "headers": { "headerName": "headerValue", ... },
        # "multiValueHeaders": { "headerName": ["headerValue", "headerValue2", ...], ... },
        "body": json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    """
    Punto de llamada de las lambda.
    """

    # Inicializa orquestador de funciones
    try:
        orquestador_lambda = OrquestadorLambda()
    except Exception as e:
        return json_response(httpStatusCode=500, body={'error':f'Error al inicializar el orquestador lambda: {e}'})

    # #! Prueba, borrar después
    # return {
    #     'statusCode' : 200,
    #     'body': str(event)# + "-----" + str(context)
    # }

    try:
        path = event['path']
        http_method = event['httpMethod']
    except Exception as e:
        path = ''
        http_method = ''
    try:
        body = event['body']
    except:
        body = {}
    try:
        content_type = event['headers']['Content-Type']
    except:
        return json_response(httpStatusCode=500, body={'error': 'Please add Content-Type header.'})

    return {
        'statusCode' : 200,
        'body': str(path) + " --30- " + str(http_method) + " --- " + str(content_type) + " --- " + str(body) + str(orquestador_lambda._convertir_body_a_dict(http_method, body)) + str(event) #+ str(resultado)
    }

    if str(path) != '' and str(http_method) != '':
        try:
            #Ejecutamos la función deseada
            resultado = orquestador_lambda.ejecutar_funcion(path, http_method, body)
            return json_response(httpStatusCode=200, body=resultado)
        except Exception as e:
            return json_response(httpStatusCode=500, body={'error': e, 'body': body, 'path': path, 'traceback': traceback.format_exc()})
    # path == ''
    return json_response(httpStatusCode=500, body={'error':'Path de la función vacío', 'path': path, 'http_method': http_method})