from twill.commands import *
from getpass import getpass
from datetime import datetime as dt, time, timedelta
import schedule
from functions import obtener_errores_de

avance = 0


def main():
    # Ingresar usuario y contraseña
    print('Creador con <3 por Dyotson (Max Militzer) y voluntarios de OSUC\n')
    print("¡NO CIERRES EL PROGRAMA HASTA QUE ESTE TOME RAMOS Y TE CONFIRME!\n")
    usuario = input("Usuario UC: ")
    password = getpass("Contraseña UC: ")
    chequeo = verificar_sesion(usuario, password)
    if chequeo[0] is False:
        exit()
    NRC = input("NRC (Separados por un espacio, Ej: 1234 1234 1234): ")
    NRC = NRC.split()
    hora = input("Ingresa la hora en formato 24 hrs (Ej: 08:00 o 16:00): ")
    if hora == 'debug':
        tomar_ramos(NRC)
    print('\n¡Toma agendada! ¡Recuerda no cerrar el programa hasta que este te confirme que tomo tus ramos!')
    reservar(usuario, password, NRC, hora)


def tomar_ramos(NRC):  # Esto debe ser de una corrida ya que usa Sessions
    # Ya logeado, printea que va a tomar ramos y redirige el output
    global avance
    avance = 16
    print('\nTomando ramos...')
    redirect_output('output.log')

    # Ingresar a Menu Principal
    go("http://ssb.uc.cl/ERPUC/twbkwbis.P_GenMenu?name=bmenu.P_MainMnu")
    avance = 32

    # Ingresar a seleccionar periodo
    go("http://ssb.uc.cl/ERPUC/bwskfreg.P_AltPin")
    a = showforms()
    semestre = a[1].fields['term_in']
    avance = 48

    # Seleccionar ultimo semestre
    fv('2', 'term_in', semestre)
    submit('0')
    avance = 64

    # Seleccionar primer plan de estudio
    b = showforms()
    plan = b[1].get_element_by_id('st_path_id').value_options
    fv('2', 'st_path', plan[1])
    submit('0')
    avance = 80

    save_html('pruebadetoma.html')
    # Aplicar NRC
    if len(NRC) == 1:
        fv('2', 'crn_id1', NRC[0])
    elif len(NRC) == 2:
        fv('2', 'crn_id1', NRC[0])
        fv('2', 'crn_id2', NRC[1])
    elif len(NRC) == 3:
        fv('2', 'crn_id1', NRC[0])
        fv('2', 'crn_id2', NRC[1])
        fv('2', 'crn_id3', NRC[2])
    submit(submit_button='Enviar Cambios')
    reset_output()
    avance = 100
    print('\n¡Ramos tomados! Ya puedes cerrar el programa... Revisa los errores a continuacion:\n')
    save_html('pruebadetoma.html')
    ramos = obtener_errores_de('pruebadetoma.html')
    for ramo in ramos:
        print(ramo[1], '-', ramo[0])
    exit()


def reservar(usuario, password, NRC, hora):
    try:
        if necesitaRelogin(hora):
            hora_login = restar_minutos(hora, minutos=5)
            schedule.every().day.at(hora_login).do(
                verificar_sesion, usuario=usuario, password=password)
        schedule.every().day.at(hora).do(tomar_ramos, NRC=NRC)
        while True:
            schedule.run_pending()
    except schedule.ScheduleValueError:
        print('Formato de hora invalido, recuerda ingresarlo en 24hrs')


def verificar_sesion(usuario, password) -> tuple:
    # (True/False, Razón)
    print('\nChequeando credenciales...')
    redirect_output('output.log')
    go('https://ssb.uc.cl/ERPUC/twbkwbis.P_WWWLogin')
    formclear('1')
    fv('1', 'sid', usuario)
    fv('1', 'PIN', password)
    submit('0')
    go("http://ssb.uc.cl/ERPUC/twbkwbis.P_GenMenu?name=bmenu.P_MainMnu")
    reset_output()
    try:
        find('Agregar o Eliminar Clases')
        print('¡Credenciales aceptadas!')
        return(True, '¡Credenciales aceptadas!')
    except:
        print('Credenciales rechazadas, porfavor intenta nuevamente')
        return(False, 'Credenciales rechazadas, porfavor intenta nuevamente')


def necesitaRelogin(hora):
    '''
    Retorna True si "hora" ocurrirá en más de 10 minutos, False en caso contrario.
        hora: Un string con la forma "%H:%M"
    '''
    actual = dt.now()
    reserva = dt.combine(actual, time.fromisoformat(hora))
    waittime = (reserva - actual).total_seconds()
    minutos_espera = 10
    if waittime >= minutos_espera*60 or waittime < 0:
        return True
    return False


def restar_minutos(hora, minutos):
    '''
    Resta a "hora" la cantidad de minutos ingresada en "minutos".
        hora: Un string con la forma "%H:%M"
        miutos: Un entero que representa la cantidad de minutos a restar
    '''
    hora_original = dt.combine(dt.now(), time.fromisoformat(hora))
    hora_con_resta = hora_original - timedelta(minutes=minutos)
    return hora_con_resta.strftime("%H:%M")


def cancelar_schedule():
    schedule.clear()


if __name__ == '__main__':
    main()
