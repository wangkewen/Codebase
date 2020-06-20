import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class ProgressMonitorTest {
    public static void main(String[] args) {
        EventQueue.invokeLater(new Runnable() {
          public void run() {
              JFrame frame = new ProgressMonitorFrame();
              frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
              frame.setVisible(true); 
          }
        });
    }
}

class ProgressMonitorFrame extends JFrame {
    private Timer cancelMonitor;
    private JButton startButton;
    private ProgressMonitor progressDialog;
    private JTextArea textArea;
    private SimulatedActivity activity;
    
    public static final int DEFAULT_WIDTH = 300;
    public static final int DEFAULT_HEIGHT = 200;

    public ProgressMonitorFrame() {
        setTitle("ProgressMonitorTest");
        setSize(DEFAULT_WIDTH, DEFAULT_HEIGHT);
        textArea = new JTextArea();
        JPanel panel = new JPanel();
        startButton = new JButton("Start");
        panel.add(startButton);
        add(new JScrollPane(textArea), BorderLayout.CENTER);
        add(panel, BorderLayout.SOUTH);

        startButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                startButton.setEnabled(false);
                final int MAX = 1000;
                activity = new SimulatedActivity(MAX);
                activity.execute();
                progressDialog = new ProgressMonitor(ProgressMonitorFrame.this,
                         "Waiting for Simulated Activity", null, 0, MAX);
                cancelMonitor.start();
            }
        });

        cancelMonitor = new Timer(500, new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                if(progressDialog.isCanceled()) {
                    activity.cancel(true);
                    startButton.setEnabled(true);
                }else if(activity.isDone()) {
                    progressDialog.close();
                    startButton.setEnabled(true);
                }else {
                    progressDialog.setProgress(activity.getProgress());
                }
            }
        });
    }

    class SimulatedActivity extends SwingWorker<Void, Integer> {
        private int current;
        private int target;
        public SimulatedActivity(int t) {
            current = 0;
            target = t;
        }
        protected Void doInBackground() throws Exception {
            try{
                while(current < target) {
                    Thread.sleep(5);
                    current += 10;
                    textArea.append(current + "\n");
                    setProgress(current);
                }
            } catch (InterruptedException e){
                e.printStackTrace();
            }
            return null;
        }
    }
}
