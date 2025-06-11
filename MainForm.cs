using System;
using System.Windows.Forms;
using System.Threading;
using OpenQA.Selenium.Appium.Windows;
using OpenQA.Selenium.Remote;
using OpenQA.Selenium.Support.UI;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Text.RegularExpressions;
using System.Linq;
using ExcelDataReader;
using Windows.UI.Xaml.Controls;
using OpenQA.Selenium;
using Keys = OpenQA.Selenium.Keys;
using System.Threading.Tasks;

namespace WhatsAppAutomator
{
    public partial class MainForm : Form
    {
        List<string> numbers = new List<string>();

        public MainForm()
        {
            InitializeComponent();
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void Log(string msg)
        {
            var text = $"[{DateTime.Now:HH:mm:ss}] {msg}{Environment.NewLine}";

            // If we’re not on the UI thread, re-invoke this method there:
            if (txtLog.InvokeRequired)
            {
                txtLog.BeginInvoke(new Action(() => Log(msg)));
                return;
            }

            // Now we’re on the UI thread—safe to update the control:
            txtLog.AppendText(text);
        }

        private void btnStart_Click(object sender, EventArgs e)
        {
            btnStart.Enabled = false;
            txtLog.Clear();

            // 1) Detect automatically
            Log("Finding WhatsApp installation…");
            string appId = WhatsAppHelper.FindInLocalAppData()
                        ?? WhatsAppHelper.FindInWindowsApps();

            // 2) Fallback: browse on the UI thread
            if (appId == null)
            {
                Log("WhatsApp Installation not found");

                using (var ofd = new OpenFileDialog())
                {
                    ofd.Title = "Locate WhatsApp.exe";
                    ofd.Filter = "WhatsApp.exe|WhatsApp.exe";
                    ofd.InitialDirectory =
                      Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);

                    if (ofd.ShowDialog() != DialogResult.OK)
                    {
                        Log("Kindly install WhatsApp Desktop to continue.");
                        btnStart.Enabled = true;
                        return;
                    }
                    appId = ofd.FileName;
                }
            }

            if (string.IsNullOrWhiteSpace(MessageBox.Text))
            {
                Log("No Message Entered");
                btnStart.Enabled = true;
                return;
            }


            if (this.numbers.Count < 1)
            {
                Log("Please load some valid numbers.");
                btnStart.Enabled = true;
                return;
            }

            btnStart.Enabled = false;
            txtLog.Clear();
            ThreadPool.QueueUserWorkItem(async _ =>
            {
                try
                {
                    Log($"Using `{appId}`");

                    Log("Ensuring WinAppDriver is running…");
                    WhatsAppHelper.LaunchWinAppDriver();

                    Log("Connecting to WinAppDriver…");
                    DesiredCapabilities appCapabilities = new DesiredCapabilities();
                    appCapabilities.SetCapability("app", appId);
                    appCapabilities.SetCapability("deviceName", "WindowsPC");

                    var driver = new WindowsDriver<WindowsElement>(new Uri("http://127.0.0.1:4723"), appCapabilities);
                    Thread.Sleep(1000);

                    var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(5));

                    // CLick title to reset UI
                    var title = wait.Until(d =>
                        driver.FindElementByAccessibilityId("LeftPanelTitleText")
                    );
                    title.Click();
                    await Task.Delay(300);

                    this.numbers = new List<string>() { "+923122978700", "+923330001963", "+923172006789" };

                    foreach (var number in this.numbers)
                    {
                        try
                        {
                            Log($"Sending message to {number}");
                            Log("Waiting for NewConvoButton…");
                            var newConvo = wait.Until(d =>
                                driver.FindElementByAccessibilityId("NewConvoButton")
                            );
                            Log("Clicking NewConvoButton…");
                            newConvo.Click();
                            await Task.Delay(300);

                            var keypad = wait.Until(d =>
                                driver.FindElementByClassName("ToggleButton")
                            );
                            Log("Clicking ToggleButton…");
                            keypad.Click();
                            await Task.Delay(300);

                            var searchBar = wait.Until(d =>
                                driver.FindElementByAccessibilityId("PhoneNumberTextBox")
                            );
                            Log("Clicking SearchBar…");
                            searchBar.Click();
                            await Task.Delay(300);

                            searchBar.SendKeys(number.Substring(3));
                            await Task.Delay(300);

                            var chatbtn = wait.Until(d =>
                                driver.FindElementsByName("Chat").FirstOrDefault()
                            );

                            if (chatbtn == null)
                            {
                                Log($"Number {number.Substring(3)} is not valid or not on WhatsApp");
                                continue;
                            }

                            Log("Clicking ChatButton…");
                            chatbtn.Click();
                            await Task.Delay(300);

                            var inputbar = wait.Until(d =>
                                driver.FindElementByAccessibilityId("InputBarTextBox")
                            );
                            Log("Clicking InputBar…");
                            inputbar.Click();
                            await Task.Delay(300);

                            var processedMessage = MessageBox.Text.Replace(Environment.NewLine, Keys.Enter.ToString());
                            inputbar.SendKeys(processedMessage);
                            await Task.Delay(300);

                            inputbar.SendKeys(Keys.Enter);
                            await Task.Delay(300);
                        }
                        catch (Exception ex)
                        {
                            Log($"Unexpected error occured {ex}");

                            // CLick title to reset UI
                            title.Click();
                            await Task.Delay(300);
                        }
                    }

                    Log("Done!  (continue with your workflow…)");
                }
                catch (Exception ex)
                {
                    Log("ERROR: " + ex.Message);
                }
                finally
                {
                    Invoke(new Action(() => btnStart.Enabled = true));
                }
            });
        }

        private async Task SendTextWithNewlines(WindowsElement inputBar, string message)
        {
            // Split the message by new lines
            var lines = message.Split(new[] { Environment.NewLine }, StringSplitOptions.None);

            foreach (var line in lines)
            {
                inputBar.SendKeys(line);    // Send the line of text
                await Task.Delay(300);      // Wait for the input to settle

                inputBar.SendKeys(Keys.Enter); // Simulate pressing Enter (to create a new line)
                await Task.Delay(300);       // Wait after sending Enter
            }
        }


        private void btnLoadExcel_Click_1(object sender, EventArgs e)
        {
            using (var ofd = new OpenFileDialog
            {
                Title = "Select your Excel file",
                Filter = "Excel files|*.xlsx;*.xls"
            })
            {
                if (ofd.ShowDialog() != DialogResult.OK)
                    return;

                var path = ofd.FileName;
                Log($"Opening Excel: {path}");

                // ExcelDataReader needs this for older .NET encodings
                // System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

                using (var stream = File.Open(path, FileMode.Open, FileAccess.Read))
                using (var reader = ExcelReaderFactory.CreateReader(stream))
                {
                    // Read into DataSet, use first row as header
                    var ds = reader.AsDataSet(new ExcelDataSetConfiguration
                    {
                        ConfigureDataTable = _ => new ExcelDataTableConfiguration { UseHeaderRow = true }
                    });
                    var table = ds.Tables[0];

                    // auto-detect “phone” column by header name
                    var phoneCol = DetectPhoneColumn(table);
                    Log($"Detected phone column: {phoneCol.ColumnName}");

                    var cleanedNumbers = new List<string>();
                    int failCount = 0;

                    foreach (DataRow row in table.Rows)
                    {
                        var raw = row[phoneCol]?.ToString() ?? "";
                        // strip spaces & hyphens
                        var num = Regex.Replace(raw, @"[\s\-]", "");

                        // normalize to +92XXXXXXXXXX
                        if (num.StartsWith("0092")) num = "+" + num.Substring(2);
                        else if (num.StartsWith("0")) num = "+92" + num.Substring(1);
                        else if (num.StartsWith("92")) num = "+" + num;
                        else if (num.StartsWith("3")) num = "+92" + num;

                        // final validation: +92 followed by exactly 10 digits
                        if (Regex.IsMatch(num, @"^\+92\d{10}$"))
                            cleanedNumbers.Add(num);
                        else
                            failCount++;
                        Log(num);
                    }

                    this.numbers = cleanedNumbers;
                    Log($"✅ Parsed {cleanedNumbers.Count} numbers, failed to parse {failCount} entries.");
                }
            }
        }

        /// <summary>
        /// Detects the most likely phone-number column in the given DataTable.
        /// 1) header keyword match
        /// 2) fuzzy match to “phone”
        /// 3) first all-numeric sample
        /// 4) fallback to first column
        /// </summary>
        private DataColumn DetectPhoneColumn(DataTable table)
        {
            var columns = table.Columns.Cast<DataColumn>().ToList();
            var headers = columns.Select(c => c.ColumnName).ToList();
            var headersLower = headers.Select(h => h.ToLowerInvariant()).ToList();

            // 1) Header‐based keyword match
            var keywords = new[] { "phone", "mobile", "contact", "cell" };
            foreach (var kw in keywords)
            {
                for (int i = 0; i < headersLower.Count; i++)
                {
                    if (headersLower[i].Contains(kw))
                        return columns[i];
                }
            }

            // 2) Fuzzy match to “phone”
            const double threshold = 0.8;
            var scores = headersLower
                .Select((h, idx) => new { idx, score = ComputeSimilarity(h, "phone") })
                .OrderByDescending(x => x.score)
                .ToList();
            if (scores[0].score >= threshold)
                return columns[scores[0].idx];

            // 3) First column whose first non‐null cell is all‐numeric (plus spaces, hyphens, parens, plus)
            var numericRx = new Regex(@"^[\d\-\+\s\(\)]+$");
            foreach (var col in columns)
            {
                var sample = table.AsEnumerable()
                                  .Select(r => r[col]?.ToString())
                                  .FirstOrDefault(s => !string.IsNullOrWhiteSpace(s));
                if (sample != null && numericRx.IsMatch(sample))
                    return col;
            }

            // 4) Last resort
            return columns.First();
        }


        /// <summary>
        /// Returns a 0–1 similarity between two strings, based on Levenshtein distance.
        /// </summary>
        private double ComputeSimilarity(string s1, string s2)
        {
            int dist = LevenshteinDistance(s1, s2);
            int maxLen = Math.Max(s1.Length, s2.Length);
            return maxLen == 0 ? 1.0 : 1.0 - (double)dist / maxLen;
        }

        private int LevenshteinDistance(string s, string t)
        {
            int n = s.Length, m = t.Length;
            var d = new int[n + 1, m + 1];

            for (int i = 0; i <= n; i++) d[i, 0] = i;
            for (int j = 0; j <= m; j++) d[0, j] = j;

            for (int i = 1; i <= n; i++)
            {
                for (int j = 1; j <= m; j++)
                {
                    int cost = s[i - 1] == t[j - 1] ? 0 : 1;
                    d[i, j] = new[]
                    {
                d[i - 1, j] + 1,      // deletion
                d[i, j - 1] + 1,      // insertion
                d[i - 1, j - 1] + cost // substitution
            }.Min();
                }
            }

            return d[n, m];
        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
