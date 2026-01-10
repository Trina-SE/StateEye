import com.crawljax.browser.EmbeddedBrowser.BrowserType;
import com.crawljax.core.CrawljaxRunner;
import com.crawljax.core.configuration.BrowserConfiguration;
import com.crawljax.core.configuration.CrawlRules;
import com.crawljax.core.configuration.CrawljaxConfiguration;
import com.crawljax.core.configuration.CrawljaxConfiguration.CrawljaxConfigurationBuilder;
import com.crawljax.plugins.crawloverview.CrawlOverview;
import com.crawljax.plugins.testcasegenerator.TestConfiguration;
import com.crawljax.plugins.testcasegenerator.TestSuiteGenerator;
import com.crawljax.stateabstractions.dom.RTEDStateVertexFactory;
import java.io.File;
import java.util.concurrent.TimeUnit;

public class DomFraggenRunner {
	public static void main(String[] args) throws Exception {
		if (args.length < 1) {
			System.err.println(
				"Usage: DomFraggenRunner <url> [runtimeMins] [maxDepth] [maxStates] [outputDir]"
			);
			System.exit(1);
		}
		String url = args[0];
		int runtimeMins = args.length >= 2 ? Integer.parseInt(args[1]) : 1;
		int maxDepth = args.length >= 3 ? Integer.parseInt(args[2]) : -1;
		int maxStates = args.length >= 4 ? Integer.parseInt(args[3]) : -1;
		String outputDir = args.length >= 5 ? args[4] : "out/dom_run";

		CrawljaxConfigurationBuilder builder = CrawljaxConfiguration.builderFor(url);

		BrowserConfiguration browserConfig = new BrowserConfiguration(BrowserType.CHROME, 1);
		builder.setBrowserConfig(browserConfig);

		builder.setStateVertexFactory(new RTEDStateVertexFactory(0.0));

		CrawlRules.CrawlRulesBuilder rules = builder.crawlRules();
		rules.setFormFillMode(CrawlRules.FormFillMode.RANDOM);
		rules.clickDefaultElements();
		rules.clickOnce(true);
		rules.crawlHiddenAnchors(false);
		rules.crawlFrames(false);
		rules.clickElementsInRandomOrder(false);
		rules.followExternalLinks(false);
		rules.waitAfterReloadUrl(500, TimeUnit.MILLISECONDS);
		rules.waitAfterEvent(500, TimeUnit.MILLISECONDS);
		rules.endRules();

		builder.setMaximumRunTime(runtimeMins, TimeUnit.MINUTES);
		if (maxDepth > 0) {
			builder.setMaximumDepth(maxDepth);
		} else {
			builder.setUnlimitedCrawlDepth();
		}
		if (maxStates > 0) {
			builder.setMaximumStates(maxStates);
		} else {
			builder.setUnlimitedStates();
		}

		builder.setOutputDirectory(new File(outputDir));
		builder.addPlugin(new CrawlOverview());
		TestConfiguration testConfig = new TestConfiguration(
			TestConfiguration.StateEquivalenceAssertionMode.DOM,
			browserConfig
		);
		builder.addPlugin(new TestSuiteGenerator(testConfig));

		CrawljaxRunner runner = new CrawljaxRunner(builder.build());
		runner.call();
	}
}
