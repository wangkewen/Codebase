import java.awt.*;
import java.util.*;
import javax.swing.*;

public class BallPaint extends JPanel {
    private ArrayList<Ball> balls = new ArrayList<>();
    
    public void add(Ball b) {
        balls.add(b);
    }
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        for(Ball b : balls) {
            float[] colors = b.getColor();
            g2d.setColor(new Color(colors[0], colors[1], colors[2]));
            g2d.fill(b.getShape());
        }
    }
}
