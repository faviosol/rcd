import java.io.DataOutputStream;
import java.net.Socket;
import java.security.SecureRandom;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class Ejemplo2Emisor {
    private static final byte[] CLAVE_SECRETA = "ClaveSecreta1234".getBytes();

    public static void main(String[] args) {
        String ipDestino = "127.0.0.1";
        int puerto = 5000;
        String mensajeOriginal = "Este mensaje contiene información confidencial."; //

        System.out.println("=== EMISOR AES-GCM iniciado. Conectando... ===");

        try (Socket socket = new Socket(ipDestino, puerto);
             DataOutputStream salida = new DataOutputStream(socket.getOutputStream())) {

            // 1. Configurar el algoritmo AES-GCM
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding"); //
            SecretKeySpec claveSpec = new SecretKeySpec(CLAVE_SECRETA, "AES");
            
            // Generar un IV (Vector de Inicialización) único de 12 bytes recomendado para GCM
            byte[] iv = new byte[12];
            new SecureRandom().nextBytes(iv);
            GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
            
            cipher.init(Cipher.ENCRYPT_MODE, claveSpec, gcmSpec);

            // 2. Cifrar el mensaje
            byte[] mensajeCifrado = cipher.doFinal(mensajeOriginal.getBytes());

            System.out.println("🔓 Mensaje original: " + mensajeOriginal);
            System.out.println("🔒 Mensaje cifrado (Hex): " + bytesToHex(mensajeCifrado));

            // 3. Enviar los datos por el socket (Primero enviamos tamaños para que el receptor sepa cuánto leer)
            salida.writeInt(iv.length);
            salida.write(iv);
            
            salida.writeInt(mensajeCifrado.length);
            salida.write(mensajeCifrado);
            
            salida.flush();
            System.out.println("🚀 Datos cifrados enviados con éxito a través del socket.");

        } catch (Exception e) {
            System.err.println("Error en el Emisor AES-GCM: " + e.getMessage());
        }
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }
}
