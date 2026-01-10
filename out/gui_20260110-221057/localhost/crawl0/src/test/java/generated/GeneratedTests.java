package generated;

import org.testng.Assert;
import org.testng.ITestResult;
import org.testng.annotations.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import com.crawljax.browser.EmbeddedBrowser.BrowserType;
import com.crawljax.core.configuration.BrowserConfiguration;
import com.crawljax.core.configuration.BrowserOptions;
import com.crawljax.core.configuration.CrawljaxConfiguration;
import com.crawljax.core.configuration.CrawljaxConfiguration.CrawljaxConfigurationBuilder;
import com.crawljax.core.state.Identification;
import com.crawljax.core.state.Identification.How;
import com.crawljax.forms.FormInput;
import com.crawljax.plugins.testcasegenerator.TestConfiguration.StateEquivalenceAssertionMode;
import com.crawljax.plugins.testcasegenerator.TestSuiteHelper;

/*
 * Generated @ Sat Jan 10 22:12:17 GMT+06:00 2026
 */

public class GeneratedTests {

    private final String URL = "http://localhost:3000/index.html";
	private TestSuiteHelper testSuiteHelper;
	
	private final String TEST_SUITE_PATH = "C:\\Users\\sulta\\Documents\\StateEye_imp\\out\\gui_20260110-221057\\localhost\\crawl0\\src\\test\\java\\generated";

	private StateEquivalenceAssertionMode assertionMode = StateEquivalenceAssertionMode.DOM;
	
	private CrawljaxConfiguration getTestConfiguration() {
		CrawljaxConfigurationBuilder builder = CrawljaxConfiguration.builderFor(URL);
		builder.crawlRules().waitAfterEvent(500, TimeUnit.MILLISECONDS);
		builder.crawlRules().waitAfterReloadUrl(500, TimeUnit.MILLISECONDS);
		builder.setBrowserConfig(new BrowserConfiguration(BrowserType.CHROME, 1, new BrowserOptions(false, -1)));
		return builder.build();
	}	
	
	@BeforeClass
	public void oneTimeSetUp(){
		try {
			//load needed data from json files
			testSuiteHelper = new TestSuiteHelper(
					getTestConfiguration(),
					"C:\\Users\\sulta\\Documents\\StateEye_imp\\out\\gui_20260110-221057\\localhost\\crawl0\\src\\test\\java\\generated\\states.json",
					"C:\\Users\\sulta\\Documents\\StateEye_imp\\out\\gui_20260110-221057\\localhost\\crawl0\\src\\test\\java\\generated\\eventables.json",
					"C:\\Users\\sulta\\Documents\\StateEye_imp\\out\\gui_20260110-221057\\localhost\\crawl0\\screenshots",
					"C:\\Users\\sulta\\Documents\\StateEye_imp\\out\\gui_20260110-221057\\localhost\\crawl0\\test-results",
					URL, TEST_SUITE_PATH);
		}
		catch (Exception e) {
			Assert.fail(e.getMessage());
		}
	}
	
	@AfterClass
	public void oneTimeTearDown(){
		try {
			testSuiteHelper.tearDown();
		}catch (Exception e) {
			Assert.fail(e.getMessage());
		}
	}

	@BeforeMethod
	public void setUp(){
		try {
			testSuiteHelper.goToInitialUrl();		
		}catch (Exception e) {
			Assert.fail(e.getMessage());
		}
	}	
	
	@AfterMethod
	public void getStatusAndDuration(ITestResult tr) {
		long duration = tr.getEndMillis() - tr.getStartMillis();
		long nanos = TimeUnit.MILLISECONDS.toNanos(duration);
		String message = "none";
		if (tr.getThrowable() != null) {
			message = tr.getThrowable().getMessage();
		}

		switch (tr.getStatus()) {
			case ITestResult.SUCCESS:
				testSuiteHelper.markLastMethodAsSucceeded(nanos);
				break;
			case ITestResult.FAILURE:
				testSuiteHelper.markLastMethodAsFailed(message, nanos);
				break;
			case ITestResult.SKIP:
				testSuiteHelper.markLastMethodAsSkipped(nanos);
				break;
		}
	}
	
	/*
	 * Test Cases
	 */
	 
	@Test(priority=1)
	public void method_0(){
		testSuiteHelper.newCurrentTestMethod("method_0");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		try {
			//initial state
			testSuiteHelper.runInCrawlingPlugins(0);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 0");

			testSuiteHelper.addStateToReportBuilder(0);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=2)
	public void method_1_2_3(){
		testSuiteHelper.newCurrentTestMethod("method_1_2_3");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[2], element=Element{node=[A: null], tag=A, text=Academics, attributes={class=nav-link, href=academics.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=3, name=state3}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "cVGJlmZq"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(1), "Event fired: Academics");
			testSuiteHelper.runInCrawlingPlugins(3);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 3");

			testSuiteHelper.addStateToReportBuilder(3);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(3)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(3)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[1], element=Element{node=[A: null], tag=A, text=Home, attributes={class=nav-link, href=index.html}}, source=RTEDStateVertexImpl{id=3, name=state3}, target=RTEDStateVertexImpl{id=0, name=index}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(2), "Event fired: Home");
			testSuiteHelper.runInCrawlingPlugins(0);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 0");

			testSuiteHelper.addStateToReportBuilder(0);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[3], element=Element{node=[A: null], tag=A, text=Events, attributes={class=nav-link, href=events.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=5, name=state5}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "LTpZNvzt"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "1"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(3), "Event fired: Events");
			testSuiteHelper.runInCrawlingPlugins(5);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 5");

			testSuiteHelper.addStateToReportBuilder(5);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(5)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(5)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=3)
	public void method_4_5_6_7(){
		testSuiteHelper.newCurrentTestMethod("method_4_5_6_7");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[4], element=Element{node=[A: null], tag=A, text=About, attributes={class=nav-link, href=about.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=8, name=state8}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "MHwGVVBy"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(4), "Event fired: About");
			testSuiteHelper.runInCrawlingPlugins(8);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 8");

			testSuiteHelper.addStateToReportBuilder(8);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(8)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(8)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[1]/A[1], element=Element{node=[A: null], tag=A, text=Return home, attributes={class=primary-btn, href=index.html}}, source=RTEDStateVertexImpl{id=8, name=state8}, target=RTEDStateVertexImpl{id=0, name=index}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(5), "Event fired: Return home");
			testSuiteHelper.runInCrawlingPlugins(0);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 0");

			testSuiteHelper.addStateToReportBuilder(0);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[1]/DIV[1]/A[1], element=Element{node=[A: null], tag=A, text=Start a Tour, attributes={class=primary-btn, href=academics.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=3, name=state3}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "DWEtPHoy"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(6), "Event fired: Start a Tour");
			testSuiteHelper.runInCrawlingPlugins(3);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 3");

			testSuiteHelper.addStateToReportBuilder(3);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(3)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(3)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[1]/A[1], element=Element{node=[A: null], tag=A, text=View events, attributes={class=ghost-btn, href=events.html}}, source=RTEDStateVertexImpl{id=3, name=state3}, target=RTEDStateVertexImpl{id=5, name=state5}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(7), "Event fired: View events");
			testSuiteHelper.runInCrawlingPlugins(5);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 5");

			testSuiteHelper.addStateToReportBuilder(5);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(5)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(5)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=4)
	public void method_1_8(){
		testSuiteHelper.newCurrentTestMethod("method_1_8");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[2], element=Element{node=[A: null], tag=A, text=Academics, attributes={class=nav-link, href=academics.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=3, name=state3}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "cVGJlmZq"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(1), "Event fired: Academics");
			testSuiteHelper.runInCrawlingPlugins(3);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 3");

			testSuiteHelper.addStateToReportBuilder(3);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(3)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(3)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[1]/BUTTON[1], element=Element{node=[BUTTON: null], tag=BUTTON, text=Design Lab, attributes={class=primary-btn, data-panel=panel-orbit}}, source=RTEDStateVertexImpl{id=3, name=state3}, target=RTEDStateVertexImpl{id=15, name=state15}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(8), "Event fired: Design Lab");
			testSuiteHelper.runInCrawlingPlugins(15);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 15");

			testSuiteHelper.addStateToReportBuilder(15);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(15)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(15)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=5)
	public void method_9(){
		testSuiteHelper.newCurrentTestMethod("method_9");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[2]/DIV[2]/A[1], element=Element{node=[A: null], tag=A, text=See events          Navigate to the events board., attributes={class=card, href=events.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=5, name=state5}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "BboLQmmy"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(9), "Event fired: See events          Navigate to the events board.");
			testSuiteHelper.runInCrawlingPlugins(5);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 5");

			testSuiteHelper.addStateToReportBuilder(5);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(5)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(5)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=6)
	public void method_4_10(){
		testSuiteHelper.newCurrentTestMethod("method_4_10");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[4], element=Element{node=[A: null], tag=A, text=About, attributes={class=nav-link, href=about.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=8, name=state8}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "MHwGVVBy"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(4), "Event fired: About");
			testSuiteHelper.runInCrawlingPlugins(8);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 8");

			testSuiteHelper.addStateToReportBuilder(8);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(8)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(8)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[1]/BUTTON[1], element=Element{node=[BUTTON: null], tag=BUTTON, text=Download map, attributes={class=secondary-btn}}, source=RTEDStateVertexImpl{id=8, name=state8}, target=RTEDStateVertexImpl{id=19, name=state19}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(10), "Event fired: Download map");
			testSuiteHelper.runInCrawlingPlugins(19);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 19");

			testSuiteHelper.addStateToReportBuilder(19);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(19)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(19)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=7)
	public void method_1_11(){
		testSuiteHelper.newCurrentTestMethod("method_1_11");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[2], element=Element{node=[A: null], tag=A, text=Academics, attributes={class=nav-link, href=academics.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=3, name=state3}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "cVGJlmZq"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(1), "Event fired: Academics");
			testSuiteHelper.runInCrawlingPlugins(3);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 3");

			testSuiteHelper.addStateToReportBuilder(3);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(3)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(3)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[1]/BUTTON[2], element=Element{node=[BUTTON: null], tag=BUTTON, text=Digital Archives, attributes={class=secondary-btn, data-panel=panel-archive}}, source=RTEDStateVertexImpl{id=3, name=state3}, target=RTEDStateVertexImpl{id=15, name=state15}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(11), "Event fired: Digital Archives");
			testSuiteHelper.runInCrawlingPlugins(15);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 15");

			testSuiteHelper.addStateToReportBuilder(15);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(15)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(15)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=8)
	public void method_12(){
		testSuiteHelper.newCurrentTestMethod("method_12");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //BUTTON[@id = 'open-spotlight'], element=Element{node=[BUTTON: null], tag=BUTTON, text=Spotlight, attributes={class=ghost-btn, id=open-spotlight}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "pyvYJWTw"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "1"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(12), "Event fired: Spotlight");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=9)
	public void method_1_13(){
		testSuiteHelper.newCurrentTestMethod("method_1_13");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[2], element=Element{node=[A: null], tag=A, text=Academics, attributes={class=nav-link, href=academics.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=3, name=state3}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "cVGJlmZq"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(1), "Event fired: Academics");
			testSuiteHelper.runInCrawlingPlugins(3);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 3");

			testSuiteHelper.addStateToReportBuilder(3);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(3)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(3)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[2]/ARTICLE[1]/BUTTON[1], element=Element{node=[BUTTON: null], tag=BUTTON, text=Preview syllabus, attributes={class=secondary-btn}}, source=RTEDStateVertexImpl{id=3, name=state3}, target=RTEDStateVertexImpl{id=15, name=state15}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(13), "Event fired: Preview syllabus");
			testSuiteHelper.runInCrawlingPlugins(15);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 15");

			testSuiteHelper.addStateToReportBuilder(15);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(15)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(15)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=10)
	public void method_14(){
		testSuiteHelper.newCurrentTestMethod("method_14");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //BUTTON[@id = 'toggle-dashboard'], element=Element{node=[BUTTON: null], tag=BUTTON, text=Open Dashboard, attributes={class=secondary-btn, id=toggle-dashboard}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "aIrAZdxn"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "1"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(14), "Event fired: Open Dashboard");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=11)
	public void method_1_15(){
		testSuiteHelper.newCurrentTestMethod("method_1_15");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[2], element=Element{node=[A: null], tag=A, text=Academics, attributes={class=nav-link, href=academics.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=3, name=state3}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "cVGJlmZq"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(1), "Event fired: Academics");
			testSuiteHelper.runInCrawlingPlugins(3);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 3");

			testSuiteHelper.addStateToReportBuilder(3);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(3)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(3)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[2]/ARTICLE[2]/BUTTON[1], element=Element{node=[BUTTON: null], tag=BUTTON, text=Join workshop, attributes={class=secondary-btn}}, source=RTEDStateVertexImpl{id=3, name=state3}, target=RTEDStateVertexImpl{id=15, name=state15}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(15), "Event fired: Join workshop");
			testSuiteHelper.runInCrawlingPlugins(15);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 15");

			testSuiteHelper.addStateToReportBuilder(15);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(15)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(15)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=12)
	public void method_16(){
		testSuiteHelper.newCurrentTestMethod("method_16");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //BUTTON[@id = 'issue-pass'], element=Element{node=[BUTTON: null], tag=BUTTON, text=Issue Pass, attributes={class=primary-btn, id=issue-pass}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "kSPFSdOB"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(16), "Event fired: Issue Pass");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=13)
	public void method_1_17(){
		testSuiteHelper.newCurrentTestMethod("method_1_17");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/HEADER[1]/NAV[1]/A[2], element=Element{node=[A: null], tag=A, text=Academics, attributes={class=nav-link, href=academics.html}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=3, name=state3}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "cVGJlmZq"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(1), "Event fired: Academics");
			testSuiteHelper.runInCrawlingPlugins(3);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 3");

			testSuiteHelper.addStateToReportBuilder(3);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(3)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(3)
					&& allStatesIdentical;
			}
			
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[2]/ARTICLE[3]/BUTTON[1], element=Element{node=[BUTTON: null], tag=BUTTON, text=Request review, attributes={class=secondary-btn}}, source=RTEDStateVertexImpl{id=3, name=state3}, target=RTEDStateVertexImpl{id=15, name=state15}} */
			Assert.assertTrue(testSuiteHelper.fireEvent(17), "Event fired: Request review");
			testSuiteHelper.runInCrawlingPlugins(15);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 15");

			testSuiteHelper.addStateToReportBuilder(15);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(15)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(15)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=14)
	public void method_18(){
		testSuiteHelper.newCurrentTestMethod("method_18");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[2]/DIV[2]/BUTTON[1], element=Element{node=[BUTTON: null], tag=BUTTON, text=Orbit Studio          Prototype lab for UI experiments., attributes={class=card, data-panel=panel-orbit}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "ppEzvIlQ"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "1"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(18), "Event fired: Orbit Studio          Prototype lab for UI experiments.");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=15)
	public void method_19(){
		testSuiteHelper.newCurrentTestMethod("method_19");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[2]/DIV[2]/BUTTON[2], element=Element{node=[BUTTON: null], tag=BUTTON, text=Archive Vault          Collections and thesis shelves., attributes={class=card, data-panel=panel-archive}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "JrfLwlAo"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(19), "Event fired: Archive Vault          Collections and thesis shelves.");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=16)
	public void method_20(){
		testSuiteHelper.newCurrentTestMethod("method_20");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath /HTML[1]/BODY[1]/MAIN[1]/SECTION[2]/DIV[2]/BUTTON[3], element=Element{node=[BUTTON: null], tag=BUTTON, text=Forum Stage          Upcoming sessions and talks., attributes={class=card, data-panel=panel-forum}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "uShXRUmI"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "1"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(20), "Event fired: Forum Stage          Upcoming sessions and talks.");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=17)
	public void method_21(){
		testSuiteHelper.newCurrentTestMethod("method_21");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //SECTION[@id = 'dashboard']/DIV[1]/BUTTON[1], element=Element{node=[BUTTON: null], tag=BUTTON, text=Discovery, attributes={class=tab active, data-tab=tab-one}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "VnUMGyDA"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(21), "Event fired: Discovery");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=18)
	public void method_22(){
		testSuiteHelper.newCurrentTestMethod("method_22");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //SECTION[@id = 'dashboard']/DIV[1]/BUTTON[2], element=Element{node=[BUTTON: null], tag=BUTTON, text=Checklist, attributes={class=tab, data-tab=tab-two}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "sapjpVvm"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "1"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(22), "Event fired: Checklist");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=19)
	public void method_23(){
		testSuiteHelper.newCurrentTestMethod("method_23");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //SECTION[@id = 'dashboard']/DIV[1]/BUTTON[3], element=Element{node=[BUTTON: null], tag=BUTTON, text=Pulse, attributes={class=tab, data-tab=tab-three}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "mKZVTqAB"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(23), "Event fired: Pulse");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=20)
	public void method_24(){
		testSuiteHelper.newCurrentTestMethod("method_24");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //BUTTON[@id = 'reserve-orbit'], element=Element{node=[BUTTON: null], tag=BUTTON, text=Reserve Slot, attributes={class=secondary-btn, id=reserve-orbit}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "FgFOIHvZ"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(24), "Event fired: Reserve Slot");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=21)
	public void method_25(){
		testSuiteHelper.newCurrentTestMethod("method_25");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //BUTTON[@id = 'request-archive'], element=Element{node=[BUTTON: null], tag=BUTTON, text=Request File, attributes={class=secondary-btn, id=request-archive}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "SPhBfoLy"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "0"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "0"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(25), "Event fired: Request File");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}

	@Test(priority=22)
	public void method_26(){
		testSuiteHelper.newCurrentTestMethod("method_26");
		List<FormInput> formInputs;
		
		boolean allStatesIdentical = true;
		
		testSuiteHelper.addStateToReportBuilder(0);

		if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(0)
									&& allStatesIdentical;
		}

		if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
		    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(0)
				&& allStatesIdentical;
		}
		try {
			/* Eventable{eventType=click, identification=xpath //BUTTON[@id = 'add-forum'], element=Element{node=[BUTTON: null], tag=BUTTON, text=Add to Agenda, attributes={class=secondary-btn, id=add-forum}}, source=RTEDStateVertexImpl{id=0, name=index}, target=RTEDStateVertexImpl{id=23, name=state23}} */
			formInputs = new ArrayList<FormInput>();
			formInputs.add(new FormInput(FormInput.InputType.TEXT, new Identification(How.id, "visitor-name"), "oELNBABJ"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[1]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[2]/INPUT[1]"), "1"));
			formInputs.add(new FormInput(FormInput.InputType.CHECKBOX, new Identification(How.xpath, "/HTML[1]/BODY[1]/MAIN[1]/SECTION[1]/DIV[2]/DIV[2]/DIV[1]/LABEL[3]/INPUT[1]"), "1"));
			testSuiteHelper.handleFormInputs(formInputs);
			Thread.sleep(100);
			Assert.assertTrue(testSuiteHelper.fireEvent(26), "Event fired: Add to Agenda");
			testSuiteHelper.runInCrawlingPlugins(23);
			Assert.assertTrue(testSuiteHelper.checkInvariants(), "Invariants satisfied in state: 23");

			testSuiteHelper.addStateToReportBuilder(23);
			
			if (assertionMode == StateEquivalenceAssertionMode.DOM || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    allStatesIdentical = testSuiteHelper.compareCurrentDomWithState(23)
									&& allStatesIdentical;
			}

			if (assertionMode == StateEquivalenceAssertionMode.VISUAL || assertionMode == StateEquivalenceAssertionMode.ALL) {
			    /* Perform a visual diff on the two states. */
			    allStatesIdentical = testSuiteHelper.compareCurrentScreenshotWithState(23)
					&& allStatesIdentical;
			}
			
		} catch (Exception e) {
			Assert.fail(e.getMessage());
		}
		if(!allStatesIdentical) {
			Assert.fail("At least one state is different.");
		}
	}


}	 
