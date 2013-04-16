import java.lang.reflect.Method;
import java.util.TreeMap;
import java.util.List;
import java.util.Map;

import org.junit.Test;
import org.junit.runner.JUnitCore;
import org.junit.runner.Request;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;
import org.junit.runners.Suite;

/**
 * 
 * @author uhl
 */
public class PyTestJUnitWrapper {

	/**
	 * Methode zum Starten des Tests auf dem Server (Horst2).
	 * 
	 * @param args
	 *            Kommandozeilenargumente: Name des auszufÃ¼hrenden Tests, oder
	 *            keins, um die Anzahl der Tests zu ermitteln.
	 */
	public static void main(final String[] args) {
		final Suite.SuiteClasses s = TestSuite.class
				.getAnnotation(Suite.SuiteClasses.class);
		final Map<String, Method> ms = new TreeMap<String, Method>();
		Request req = null;
		Result res = null;
		for (Class<?> cl : s.value()) {
			for (Method m : cl.getMethods()) {
				final Test t = m.getAnnotation(Test.class);
				if (t != null) {
					ms.put(m.getDeclaringClass().getName() + "_" + m.getName(),
							m);
				}
			}
		}

		Method[] methods = ms.values().toArray(new Method[0]);

		if (args.length == 1) {
			final int testNumber = Integer.parseInt(args[0]);

			if (testNumber >= 0 && testNumber < methods.length) {
				try {
					req = Request.method(
							methods[testNumber].getDeclaringClass(),
							methods[testNumber].getName());
					res = new JUnitCore().run(req);
					final int testFails = res.getFailureCount();
					final List<Failure> failures = res.getFailures();
					for (Failure f : failures) {
						System.out.println(f.getDescription());
					}
					System.exit(testFails);
				} catch (Exception e) {
					System.exit(1);
				}
			} else {
				System.exit(1);
			}

		} else {

			int testCount = 0;

			for (Method m : methods) {
				final Test t = m.getAnnotation(Test.class);
				if (t != null) {
					final Testdescription d = m
							.getAnnotation(Testdescription.class);
					if (d != null) {
						System.out.print(d.value());
						System.out.print(" - ");
					}
					System.out.print(m.getDeclaringClass().getName());
					System.out.print("_");
					System.out.println(m.getName());

					testCount++;
				}
			}
			System.exit(testCount);

		}
	}

}
