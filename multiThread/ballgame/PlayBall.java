import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.util.*;
import java.util.concurrent.*;

public class PlayBall {
   public static void main(String[] args) {
        EventQueue.invokeLater(new Runnable() {
            public void run() {
                JFrame frame = new PlayGround();
                frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
                frame.setVisible(true);
            }
        });
    }
}

class PlayGround extends JFrame {
    private BallPaint ballpaint;
    private ArrayList<BallRunnable> balls;
    private int pauseCount = 0;
    private ExecutorService exec;
    public static final int DEFAULT_WIDTH = 450;
    public static final int DEFAULT_HEIGHT = 350;
    
    public PlayGround() {
        setSize(DEFAULT_WIDTH, DEFAULT_HEIGHT);
        setTitle("Ball Playground");
        ballpaint = new BallPaint();
        balls = new ArrayList<BallRunnable>();
        exec = Executors.newCachedThreadPool();
        add(ballpaint, BorderLayout.CENTER);
        JPanel buttonPanel = new JPanel();
        
        addButton(buttonPanel, "Play", new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                addBall();
            }
        });
        addButton(buttonPanel, "Close", new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                System.exit(0); 
            }
        });
        addButton(buttonPanel, "Pause", new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                if(pauseCount %2 == 0)
                    pauseBall();
                else resumeBall();
                pauseCount++;
            }
        });

        add(buttonPanel, BorderLayout.SOUTH);
    }

    public void addButton(Container c, String title, ActionListener listener) {
        JButton button = new JButton(title);
        c.add(button);
        button.addActionListener(listener);
    }
    public void addBall() {
        Ball b = new Ball();
        ballpaint.add(b);
        BallRunnable r = new BallRunnable(b, ballpaint);
        balls.add(r);
        exec.execute(r);
    }
    public void pauseBall() {
        for(BallRunnable b : balls) b.suspend();
    }
    public void resumeBall() {
        for(BallRunnable b: balls) b.resume();
    }
}

class BallRunnable implements Runnable {
    private Ball ball;
    private Component component;
    private boolean suspend;
    public static final int STEPS = 2000;
    public static final int DELAY = 2;

    public BallRunnable(Ball ball, Component component) {
        this.ball = ball;
        this.component = component;
    }
    public void run() {
        try {
            for(int i = 1; i<= STEPS; i++){
                synchronized(this) {
                    while(suspend) wait();
                }
                ball.move(component.getBounds());
                component.repaint();
                System.out.println("ball run "+i);
                Thread.sleep(DELAY);
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
    public void suspend() {
        suspend = true;
    }
    public synchronized void resume() {
        suspend = false;
        notify();
    }
}
