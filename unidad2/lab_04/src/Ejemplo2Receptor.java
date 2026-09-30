import java.io.DataInputStream;
import java.net.ServerSocket;
import java.net.Socket;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class Ejemplo2Receptor {
    // La clave debe ser exactamente de 16 bytes (128 bits) para AES-128
    private static final byte[] CLAVE_SECRETA = "ClaveSecreta1234".getBytes();

    public static void main(String[] args) {
        int puerto = 5000;
        System.out.println("=== RECEPTOR AES-GCM iniciado. Esperando conexión... ===");

        try (ServerSocket servidor = new ServerSocket(puerto);
             Socket socket = servidor.accept();
             DataInputStream entrada = new DataInputStream(socket.getInputStream())) {

            // 1. Leer la longitud del IV y el IV mismo
            int longitudIV = entrada.readInt();
            byte[] iv = new byte[longitudIV];
            entrada.readFully(iv);

            // 2. Leer la longitud del mensaje cifrado y el contenido cifrado
            int longitudCifrado = entrada.readInt();
            byte[] mensajeCifrado = new byte[longitudCifrado];
            entrada.readFully(mensajeCifrado);

            System.out.println("\n[DATOS RECIBIDOS DESDE LA RED]:");
            System.out.println("📦 IV (Hex): " + bytesToHex(iv));
            System.out.println("📦 Texto Cifrado (Hex): " + bytesToHex(mensajeCifrado));

            // 3. Configurar el descifrado AES-GCM
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding"); //
            SecretKeySpec claveSpec = new SecretKeySpec(CLAVE_SECRETA, "AES");
            // GCM usa una etiqueta de autenticación de 128 bits (16 bytes) por defecto
            GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
            cipher.init(Cipher.DECRYPT_MODE, claveSpec, gcmSpec);

            // 4. Descifrar el mensaje
            byte[] mensajeDescifradoBytes = cipher.doFinal(mensajeCifrado);
            String mensajeOriginal = new String(mensajeDescifradoBytes);

            System.out.println("\n[PROCESO DE DESCIFRADO EXITOSO]:");
            System.out.println("🔓 Mensaje recuperado: " + mensajeOriginal);

        } catch (javax.crypto.AEADBadTagException e) {
            System.err.println("\n❌ ¡ERROR DE AUTENTICACIÓN!: El mensaje fue alterado o la clave es incorrecta."); //
        } catch (Exception e) {
            System.err.println("Error en el Receptor AES-GCM: " + e.getMessage());
        }
    }

    // Función auxiliar para mostrar los bytes en formato legible (Hexadecimal)
    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }
}
