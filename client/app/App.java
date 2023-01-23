package client.app;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.swing.JFileChooser;
import javax.swing.UIManager;
import javax.swing.UnsupportedLookAndFeelException;
import javax.swing.UIManager.LookAndFeelInfo;

public class App {
    private static final String HOST = "127.0.0.1";
    private static final int PORT = 8585;

    private static DataOutputStream dout;
    private static DataInputStream din;
    private static Scanner scanner;

    
    public static void main(String[] args) {
        try {
            changeLookGUI();

            Socket socket = new Socket(HOST, PORT);

            System.out.println("🚀 - Conectado ao servidor!");

            dout = new DataOutputStream(socket.getOutputStream());  
            din = new DataInputStream(socket.getInputStream());

            scanner = new Scanner(System.in);

            int option = 0;

            while(option != 3) {
                System.out.println("Escolha uma opção: ");
                System.out.println("[1] - Enviar arquivo");
                System.out.println("[2] - Receber arquivo");
                System.out.println("[3] - Encerrar o programa");

                System.out.print("> ");
                option = Integer.parseInt(scanner.nextLine());

                switch (option) {
                    case 1:
                        sendFile();
                        break;
                    case 2:
                        receiveFile();
                        break;
                    case 3: break;
                    default:
                        System.out.println("❌ - Opção inválida!");
                        break;
                }
            }

            exit(socket);
        } catch (IOException e) {
            Logger.getLogger(ServerSocket.class.getName()).log(Level.SEVERE, e.getMessage() != null ? "❌ - Não foi possível conectar ao servidor!" : e.getMessage());
        }
    }

    private static void sendFile() throws IOException {
        JFileChooser fileChooser = new JFileChooser();
        
        int responseFileChooser = fileChooser.showOpenDialog(null);

        String response;

        if(responseFileChooser == JFileChooser.APPROVE_OPTION) {
            File selectedFile = fileChooser.getSelectedFile();
            String filePath = selectedFile.getAbsolutePath();

            Map<String, String> req = clientRequest("send", filePath);

            dout.writeUTF(req.toString());

            response = din.readUTF();
            System.out.println("📢 - " + response);
            dout.flush();
        }
    }

    private static void receiveFile() throws IOException {
        String response;
        String clientPath = new File(".").getCanonicalPath() + "/client";

        Map<String, String> req = clientRequest("receive", clientPath);

        dout.writeUTF(req.toString());
        response = din.readUTF();
        System.out.println("📢 - " + response);
        dout.flush();
    }

    private static void changeLookGUI() {
        try {
            for (LookAndFeelInfo info : UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus".equals(info.getName())) {
                    UIManager.setLookAndFeel(info.getClassName());
                    break;
                }
            }
        } catch (Exception e) {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (ClassNotFoundException | InstantiationException | IllegalAccessException | UnsupportedLookAndFeelException ex) {
                ex.printStackTrace();
            }
        }
    }

    private static Map<String, String> clientRequest(String type, String data) {
        Map<String, String> clientRequest = new HashMap<>();

        clientRequest.put("type", type);
        clientRequest.put("data", data);

        return clientRequest;
    }

    private static void exit(Socket socket) {
        try {
            Map<String, String> req = clientRequest("exit", "Desconectou!");
            
            dout.writeUTF(req.toString());

            dout.close();
            din.close();
            scanner.close();
            socket.close();
            System.exit(0);
        } catch (Exception e) {
            System.out.println("❌ - Erro ao sair do programa!");
        }
    }
}
