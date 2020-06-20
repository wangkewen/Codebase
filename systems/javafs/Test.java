public class Test {
    public static void main(String[] args) {
        Integer a = new Integer(3);
        System.out.println(a.getClass());
        System.out.println(a.getClass().getComponentType());
        System.out.println(a.getClass().getName());
        System.out.println(Integer.TYPE);
        System.out.println(a.getClass().isPrimitive());
    }
}
