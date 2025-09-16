using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Windows.Forms;

namespace WhatsAppAutomator
{
    static class WhatsAppHelper
    {
        public static void LaunchWinAppDriver()
        {
            try
            {
                Process.Start(
                    @"C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe");
                Thread.Sleep(500);
            }
            catch { /* assume already running */ }
        }

        public static string FindWhatsappExe()
        {
            // 1) Try LocalAppData\WhatsApp\app-*\WhatsApp.exe
            var exe = FindInLocalAppData();
            if (exe != null) return exe;

            // 2) Try Microsoft Store install under WindowsApps
            exe = FindInWindowsApps();
            if (exe != null) return exe;

            // 3) Fallback: let the user pick it
            using (var ofd = new OpenFileDialog())
            {
                ofd.Title = "Locate WhatsApp.exe";
                ofd.Filter = "WhatsApp.exe|WhatsApp.exe";
                ofd.InitialDirectory =
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);

                if (ofd.ShowDialog() == DialogResult.OK)
                    return ofd.FileName;
            }

            return null;
        }

        public static string FindInLocalAppData()
        {
            var local = Environment.GetFolderPath(
                Environment.SpecialFolder.LocalApplicationData);
            var baseDir = Path.Combine(local, "WhatsApp");
            if (!Directory.Exists(baseDir)) return null;

            var versionDirs = Directory
                .GetDirectories(baseDir, "app-*")
                .OrderBy(dir =>
                {
                    // parse “app-1.2.3” → [1,2,3]
                    var parts = Path.GetFileName(dir)
                                   .Substring(4)
                                   .Split('.')
                                   .Select(int.Parse)
                                   .ToArray();
                    // combine to a single sortable key
                    return ((long)parts[0] << 32)
                         | ((long)parts[1] << 16)
                         | parts[2];
                })
                .ToList();

            if (!versionDirs.Any()) return null;
            var latest = versionDirs.Last();
            var exePath = Path.Combine(latest, "WhatsApp.exe");
            return File.Exists(exePath) ? exePath : null;
        }

        public static string FindInWindowsApps()
        {
            // the protected folder where MS-Store apps live
            var winApps = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                "WindowsApps");
            if (!Directory.Exists(winApps)) return null;

            // look for the WhatsAppDesktop package(s)
            var pkgDirs = Directory
                .GetDirectories(winApps, "5319275A.WhatsAppDesktop_*")
                .OrderBy(d => d)   // lexicographically; should roughly sort by version
                .ToArray();

            if (!pkgDirs.Any()) return null;

            var latestFolder = Path.GetFileName(pkgDirs.Last());
            // e.g. "5319275A.WhatsAppDesktop_2.2324.1.0_x64__cv1g1gvanyjgm"

            // 4) split on the double-underscore into [name_version_arch] and [publisherID]
            var parts = latestFolder.Split(new[] { "__" }, StringSplitOptions.None);
            if (parts.Length != 2)
                return null;

            // parts[0] == "5319275A.WhatsAppDesktop_2.2324.1.0_x64"
            // parts[1] == "cv1g1gvanyjgm"

            // 5) get the base package name before the version segment:
            var nameBase = parts[0].Split('_')[0];
            // nameBase == "5319275A.WhatsAppDesktop"

            // 6) build the PackageFamilyName
            var familyName = $"{nameBase}_{parts[1]}";
            // e.g. "5319275A.WhatsAppDesktop_cv1g1gvanyjgm"

            // 7) finally append the ApplicationId ("App" in WhatsApp's manifest)
            return $"{familyName}!App";
        }
    }
}
