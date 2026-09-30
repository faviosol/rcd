import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

public class Ejemplo1Receptor {
    public static void main(String[] args) {
        int puerto = 5000;
        System.out.println("[Receptor] Esperando conexión en el puerto " + puerto + "...");
        
        try (ServerSocket servidor = new ServerSocket(puerto);
             Socket socket = servidor.accept();
             BufferedReader entrada = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
            
            System.out.println("[Receptor] ¡Emisor conectado!");
            String mensajeRecibido = entrada.readLine();
            System.out.println("[Receptor] Mensaje original recibido: " + mensajeRecibido);
            
        } catch (Exception e) {
            System.err.println("[Receptor] Error: " + e.getMessage());
        }
    }
}
