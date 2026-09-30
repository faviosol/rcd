import java.io.PrintWriter;
import java.net.Socket;

public class Ejemplo1Emisor {
    public static void main(String[] args) {
        String host = "127.0.0.1"; // Tu propia máquina (Loopback)
        int puerto = 5000;
        String mensaje = "Este mensaje contiene información confidencial.";
        
        System.out.println("[Emisor] Conectando a " + host + ":" + puerto + "...");
        
        try (Socket socket = new Socket(host, puerto);
             PrintWriter salida = new PrintWriter(socket.getOutputStream(), true)) {
            
            System.out.println("[Emisor] Enviando mensaje...");
            salida.println(mensaje);
            System.out.println("[Emisor] ¡Mensaje enviado con éxito!");
            
        } catch (Exception e) {
            System.err.println("[Emisor] Error al conectar: " + e.getMessage());
        }
    }
}
