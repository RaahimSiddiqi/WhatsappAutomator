namespace WhatsAppAutomator
{
    partial class MainForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.btnStart = new System.Windows.Forms.Button();
            this.txtLog = new System.Windows.Forms.TextBox();
            this.btnLoadExcel = new System.Windows.Forms.Button();
            this.lblPrompt = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.MessageBox = new System.Windows.Forms.TextBox();
            this.attach_image = new System.Windows.Forms.Button();
            this.radioButton1 = new System.Windows.Forms.RadioButton();
            this.prepend_image = new System.Windows.Forms.RadioButton();
            this.toolTip1 = new System.Windows.Forms.ToolTip(this.components);
            this.panel1 = new System.Windows.Forms.Panel();
            this.panel2 = new System.Windows.Forms.Panel();
            this.panel1.SuspendLayout();
            this.panel2.SuspendLayout();
            this.SuspendLayout();
            // 
            // btnStart
            // 
            this.btnStart.AccessibleName = "btnStart";
            this.btnStart.Location = new System.Drawing.Point(29, 75);
            this.btnStart.Name = "btnStart";
            this.btnStart.Size = new System.Drawing.Size(117, 41);
            this.btnStart.TabIndex = 1;
            this.btnStart.Text = "Launch";
            this.btnStart.UseVisualStyleBackColor = true;
            this.btnStart.Click += new System.EventHandler(this.btnStart_Click);
            // 
            // txtLog
            // 
            this.txtLog.AccessibleName = "txtLog";
            this.txtLog.Location = new System.Drawing.Point(58, 276);
            this.txtLog.Multiline = true;
            this.txtLog.Name = "txtLog";
            this.txtLog.ReadOnly = true;
            this.txtLog.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtLog.Size = new System.Drawing.Size(683, 208);
            this.txtLog.TabIndex = 3;
            // 
            // btnLoadExcel
            // 
            this.btnLoadExcel.Location = new System.Drawing.Point(29, 25);
            this.btnLoadExcel.Name = "btnLoadExcel";
            this.btnLoadExcel.Size = new System.Drawing.Size(117, 44);
            this.btnLoadExcel.TabIndex = 4;
            this.btnLoadExcel.Text = "Load Excel File";
            this.btnLoadExcel.UseVisualStyleBackColor = true;
            this.btnLoadExcel.Click += new System.EventHandler(this.btnLoadExcel_Click_1);
            // 
            // lblPrompt
            // 
            this.lblPrompt.AccessibleName = "lblPrompt";
            this.lblPrompt.AutoSize = true;
            this.lblPrompt.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.2F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblPrompt.Location = new System.Drawing.Point(284, 19);
            this.lblPrompt.Name = "lblPrompt";
            this.lblPrompt.Size = new System.Drawing.Size(227, 20);
            this.lblPrompt.TabIndex = 0;
            this.lblPrompt.Text = "WhatsAppNumber Automator";
            this.lblPrompt.Click += new System.EventHandler(this.label1_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Cursor = System.Windows.Forms.Cursors.Default;
            this.label1.Location = new System.Drawing.Point(55, 257);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(33, 16);
            this.label1.TabIndex = 5;
            this.label1.Text = "Log:";
            this.label1.Click += new System.EventHandler(this.label1_Click_1);
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(274, 72);
            this.label2.Name = "label2";
            this.label2.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.label2.Size = new System.Drawing.Size(64, 16);
            this.label2.TabIndex = 6;
            this.label2.Text = "Message";
            this.toolTip1.SetToolTip(this.label2, "\\");
            this.label2.Click += new System.EventHandler(this.label2_Click);
            // 
            // MessageBox
            // 
            this.MessageBox.AccessibleName = "messageBox";
            this.MessageBox.Location = new System.Drawing.Point(274, 91);
            this.MessageBox.MaxLength = 1024;
            this.MessageBox.Multiline = true;
            this.MessageBox.Name = "MessageBox";
            this.MessageBox.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.MessageBox.Size = new System.Drawing.Size(467, 175);
            this.MessageBox.TabIndex = 7;
            this.MessageBox.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // attach_image
            // 
            this.attach_image.Location = new System.Drawing.Point(11, 6);
            this.attach_image.Name = "attach_image";
            this.attach_image.Size = new System.Drawing.Size(95, 27);
            this.attach_image.TabIndex = 8;
            this.attach_image.Text = "Attach Image";
            this.attach_image.UseVisualStyleBackColor = true;
            this.attach_image.Click += new System.EventHandler(this.attach_image_Click);
            // 
            // radioButton1
            // 
            this.radioButton1.AutoSize = true;
            this.radioButton1.Location = new System.Drawing.Point(97, 35);
            this.radioButton1.Name = "radioButton1";
            this.radioButton1.Size = new System.Drawing.Size(76, 20);
            this.radioButton1.TabIndex = 9;
            this.radioButton1.TabStop = true;
            this.radioButton1.Text = "Append";
            this.radioButton1.UseVisualStyleBackColor = true;
            // 
            // prepend_image
            // 
            this.prepend_image.AccessibleName = "prepend_image";
            this.prepend_image.AutoSize = true;
            this.prepend_image.Location = new System.Drawing.Point(11, 35);
            this.prepend_image.Name = "prepend_image";
            this.prepend_image.Size = new System.Drawing.Size(80, 20);
            this.prepend_image.TabIndex = 10;
            this.prepend_image.TabStop = true;
            this.prepend_image.Text = "Prepend";
            this.prepend_image.UseVisualStyleBackColor = true;
            this.prepend_image.CheckedChanged += new System.EventHandler(this.prepend_image_CheckedChanged);
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.attach_image);
            this.panel1.Controls.Add(this.radioButton1);
            this.panel1.Controls.Add(this.prepend_image);
            this.panel1.Location = new System.Drawing.Point(611, 6);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(177, 62);
            this.panel1.TabIndex = 11;
            // 
            // panel2
            // 
            this.panel2.Controls.Add(this.btnLoadExcel);
            this.panel2.Controls.Add(this.btnStart);
            this.panel2.Location = new System.Drawing.Point(58, 91);
            this.panel2.Name = "panel2";
            this.panel2.Size = new System.Drawing.Size(171, 146);
            this.panel2.TabIndex = 12;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(800, 486);
            this.Controls.Add(this.panel2);
            this.Controls.Add(this.panel1);
            this.Controls.Add(this.MessageBox);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.txtLog);
            this.Controls.Add(this.lblPrompt);
            this.Name = "MainForm";
            this.Text = "Form1";
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.panel2.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Button btnStart;
        private System.Windows.Forms.TextBox txtLog;
        private System.Windows.Forms.Button btnLoadExcel;
        private System.Windows.Forms.Label lblPrompt;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox MessageBox;
        private System.Windows.Forms.Button attach_image;
        private System.Windows.Forms.RadioButton radioButton1;
        private System.Windows.Forms.RadioButton prepend_image;
        private System.Windows.Forms.ToolTip toolTip1;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Panel panel2;
    }
}

