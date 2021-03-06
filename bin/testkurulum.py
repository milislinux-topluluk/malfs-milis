#!/usr/bin/python3

# Milis Linux Konsol Kurulum Betiği
# Dialog manuali için: http://pythondialog.sourceforge.net/doc/

import os,sys,re,subprocess,time
## For legacy isos.
os.system("mps -GG")
if os.path.exists("/usr/bin/pip3") is False:
	os.system("mps -G")
	time.sleep(3)
	os.system("mps kur python3-pip && pip3 install pythondialog")
if os.path.exists("/usr/bin/acp") is False:
	os.system("mps -G")
	time.sleep(3)
	os.system("mps kur advcp")
#lsb-release tamiri
time.sleep(3)
os.system("mps -sz lsb-release && mps -ik lsb-release")

from dialog import Dialog

d = Dialog(dialog="dialog")
log = open("/tmp/kurulum.log","w")

def runShellCommand(c):
	out = subprocess.check_output(c,stderr=subprocess.STDOUT,shell=True,universal_newlines=True)
	return out.replace("\b","")  #encode byte format to string, ugly hack 

def isEFI():
	return os.path.isdir("/sys/firmware/efi")

def greetingDialog():
	greeting = """
	Milis GNU/Linux kurulum aracı Milis'i bilgisayarınıza güvenli bir şekilde kurmanızı sağlamak amacıyla geliştirilmiş basit bir kurulum aracıdır.


	Bu araç sayesinde disklerinizi bölümlendirebilir, sistemi kuracağınız ve takas alanı için kullanacağınız disk bölümünü seçebilir, kullanıcı oluşturma ve diğer bazı sistem ayarlarını yapabilirsiniz. 

	Deneyimsiz kullanıcılar için kuruluma başlamadan önce https://milis.gungre.ch/kurulum.html adresine bakmalarını öneririz.


	Kuruluma devam etmek istiyor musunuz ?
	"""
	status = d.yesno(title="Milis GNU/Linux kurulum aracına hoş geldiniz !",text=greeting,width=70,height=22)
	if status == "ok":
		checkUsername()
	else:
		sys.exit()

def checkUsername():
	
	#status ok ya da cancel gibi durumları çekiyor. 
	status,username = d.inputbox(title="Adım 1: Kullanıcı İşlemleri",text="Sistemi daha güvenli ve sağlıklı bir şekilde kullanabilmeniz açısından normal bir kullanıcı hesabına ihtiyacınız vardır ve bu zorunlu bir adımdır. \n\n \
	Bu kullanıcı güvenlik nedeniyle bazı işlemler için kısıtlı yetkilere sahiptir fakat bunu gerektiğinde \'sudo <komut_adi>\' komutuyla yükseltebilirsiniz. \n\n Sudo komutu sizden  \
	her oturum için bir kereye mahsus olarak kullanıcı şifrenizi ister. Bu yüzden kullanıcı şifreniz güçlü ama akılda kalıcı olmalıdır ve bunu paylaşmamalısınız. Daha fazla bilgi için manual dosyalarına bakabilirsiniz.\n\n\
	Lütfen kullanıcı adı giriniz:",width=70,height=22)
	
	#NAME_REGEX bkz. man 5 adduser.conf
	if re.compile(r'^[a-z][-a-z0-9]*$').match(username):
		checkUserPassword(username)
	else:
		status=d.msgbox(title="Hata !",text="\nHatalı kullanıcı adı girdiniz.\n\n\
		Kullanıcı adları alfanümerik karakterle başlamalıdır ve alfanümerik (a-z), nümerik (0-9) ve tire (-) \
		harici bir karakter içermemelidir.",width=70,height=13)
		if status == "ok":
			checkUsername()


def createUser(name,username,password):
	status,name = d.inputbox(title="Adım 1: Kullanıcı İşlemleri",text="Kullanıcı'nın adını giriniz. Eğer kullanıcının adını girmek istemiyorsanız, basitçe boş bırakın.",width=70)
	os.system("kopar '"+name+"' "+username)
	os.system('echo -e "'+password+'\n'+password+'" | passwd '+username)
	os.system('cp -r /root/.config /home/{}'.format(username))
	os.system('cp /root/.xinitrc /home/{}'.format(username))

def checkUserPassword(username):
	#insecure=True parolanın yıldız şeklinde gözükmesini sağlar, 
	#root şifresi sorarken belki bunu silebiliriz normal sudo şifresi 
	#girer gibi gözükmez. 
	status,password = d.passwordbox(title="Adım 1: Kullanıcı İşlemleri",text="Lütfen {} kullanıcısı için şifrenizi giriniz. \n\n".format(username),insecure=True,width=70,height=10)
	if len(password) > 0:
		createUser(username,username,password)
		log.write("[+] Kullanıcı eklendi: {} \n\n".format(username))
		if d.yesno(title="Adım 1: Kullanıcı İşlemleri",text="{} kullanıcısı başarıyla eklendi.\n\nYeni kullanıcı eklemek istiyor musunuz ?".format(username),width=70,height=10) == "ok":
			checkUsername()
		else:
			chRootPass()
	else:
		status=d.msgbox(title="Hata !",text="Şifreniz boş olamaz")
		checkUserPassword(username)
def chRootPass():
	status,password = d.passwordbox(title="Adım 1: Kullanıcı İşlemleri",text="Lütfen root kullanıcısı için şifrenizi giriniz. Şifre ekranda görünmeyecektir. \n\n",insecure=False,width=70,height=10)
	if len(password) > 0:
		os.system('echo -e "'+password+'\n'+password+'" | passwd root')
		chooseDisk()
	else:
		status=d.msgbox(title="Hata !",text="Şifreniz boş olamaz")
def chooseDisk():
	diskChoice = []
	diskNames  = runShellCommand("lsblk -nS -o NAME").split('\n')
	diskModels = runShellCommand("lsblk -nS -o MODEL").split('\n')
	for i in range(len(diskNames)):
		diskChoice.append((diskNames[i],diskModels[i]))
	log.write("Sistemdeki diskler: \n")
	for disq in diskChoice:
		log.write("{} \t {}\n".format(disq[0],disq[1]))
	status,selectedDisk = d.menu(title="Adım 2: Disk İşlemleri",text="Lütfen bölümleme yapmak istediğiniz diski seçiniz:",choices=diskChoice,width=70)
	log.write("\n[+] Seçilmiş Disk: {}\n\n".format(selectedDisk))
	if isEFI():
		d.msgbox(title="Uyarı !",text="(U)EFI kullanan bir sistem kullanıyorsunuz.\n\n \
		Kurulum aracımız (U)EFI desteklemekle birlikte henüz deneysel bir özelliktir ve kurulum \
		sonrası yaşanacak veri kayıplarından kullanıcı sorumludur.\
		Eğer sisteminizde hali hazırda EFI kullanan başka bir işletim sistemi varsa muhtemelen  \
		diski GPT olarak bölümlemenize ve EFI bölümünü elle oluşturmanıza gerek kalmayacaktır. \
		Eğer sanal makinaya ya da boş bir diske kuruyorsanız ve ne yapacağınızı bilmiyorsanız \
		https://milis.gungre.ch/efikurulum.html adresindeki makaleye göz atınız.",width=70,height=22)
	os.system("cfdisk /dev/" + selectedDisk)
	choosePart()


def choosePart():
	partChoice = []
	validParts = ['sd','hd','mmcblk0p']
	#Şimdilik Parted kütüphanesine gerek kalmadı, lsblk istediğimiz bütün değerleri alıyor.
	diskParts  = runShellCommand("lsblk -ln -o  NAME    | awk '{print $1}'").split('\n')
	partSizes  = runShellCommand("lsblk -ln -o  SIZE    | awk '{print $1}'").split('\n')
	partFs     = runShellCommand("lsblk -ln -o  FSTYPE  | awk '{print $1}'").split('\n')
	partMajmin = runShellCommand("lsblk -ln -o  MAJ:MIN | awk '{print $1}'").split('\n')
	partLabel  = runShellCommand("lsblk -ln -o  LABEL").split('\n') #Bunda awk yok çünkü arada boşluk olabilir. 
	for i in range(len(diskParts)-1):
		if partMajmin[i].split(":")[1] != "0": # partition olmayanları ele (sda/sdb seçince grub bozuluyor.)
			for validPart in validParts:
				if validPart in diskParts[i]: 
					partChoice.append((diskParts[i],partLabel[i]+ "\t" +partSizes[i]+"\t"+partFs[i]))
	log.write("Sistemdeki disk bölümleri: \n")
	for disqPart in partChoice:
		log.write("{} {}\n".format(disqPart[0],disqPart[1])) 
	status,selectedPart = d.menu(title="Adım 2: Disk İşlemleri",text="Sistemin kurulacağı diski seçiniz:",choices=partChoice,width=70)
	if status == "ok":
		log.write("[+] Seçilen disk bölümü: {}\n".format(selectedPart))
		formatDialog(selectedPart)
def formatDialog(part):
	status = d.yesno(title="Uyarı !", 
	text="/dev/{} bölümü ext4 türünde formatlanacak. Emin misiniz ?".format(part),width=70)	
	if status == "ok":
		d.infobox(text="Formatlanıyor... Lütfen bekleyiniz...")
		formatPart(part)
	else:
		choosePart() 
		
def formatPart(part):
	target="/dev/{}".format(part)
	os.system("umount {}".format(target))
	os.system("mkfs.ext4 {}".format(target))
	log.write("Disk bölümü formatlandı: {}\n".format(part))
	d.infobox(text="/dev/{} Disk Formatlandı".format(part))
	status = d.yesno(title="Adım 2: Disk İşlemleri",text="Takas alanı (Swap) bellekteki (RAM) sabit disk üzerinde işletim sistemi tarafından ayrılmış bir bölümdür. \
	İşlenecek veriler RAM'e sığmadığı zaman bu bölüm RAM gibi kullanılır ve böylece işlemlerin devam etmesi sağlanır. \
	Sabit disklerin veri okuma/yazma hızları RAM'lerden çok daha düşük olduğu için takas alanının kullanılması işlemleri yavaşlatabilir.\n\n\
	Düşük belleğe sahip bilgisayarlar için önerilir. Eğer diskinizde bu amaç için hali hazırda 1GB kadar yer ayırdıysanız Evet'i aksi takdirde Hayır'ı seçiniz.".format(part),width=70,height=15)	
	if status == "ok":
		chooseSwap(part)
	mountTarget(target)

def mountTarget(target):
	os.system("mount "+target+" /mnt")
	log.write('[+] Hedef mount edildi.')
	applySettings()
	d.infobox(title="Adım 4: Dosya kopyalama",text="Hedef disk sorunsuzca bağlandı. Şimdi dosyalar kopyalanacak !!",width=70)
	time.sleep(3)	
	copySystemFiles(target)

def applySettings():
	status,hostname = d.inputbox(title="Adım 3: Konfigürasyonlar",text="Hostname'i bilgisayar adı olarak düşünebilirsiniz. Bu ismi ağ cihazlarında ya da konsolda çalışırken görebilirsiniz. Lütfen hostname giriniz: ",width=70)
	os.system("echo '{}' > /etc/hostname".format(hostname))


def copySystemFiles(target):
	os.system("clear")
	os.system("acp -gaxnu /  /mnt")
	log.write('[+] Dosyalar kopyalandı.\n')
	initramfsCreate(target)
	
def initramfsCreate(target):
	os.system('chroot /mnt dracut --no-hostonly --add-drivers "ahci" -f /boot/initramfs')
	log.write('[+] Initramfs oluşturuldu.')

	if d.yesno(title="Adım 4: Önyükleyici kurulumu",text=" GNU/GRUB, Linux ve Windows gibi diğer işletim sistemlerini yüklemek için kullanılan bir önyükleyicidir. Bu Milis'i açabilmek için gerekli bir adımdır\
		fakat ne yaptığınızı biliyorsanız bir nedenden ötürü grub kurmak istemeyebilirsiniz.\n\n  Grub önyükleyiciyi kurmak istiyor musunuz ?",width=70) == "ok":
		installGrub(target)
	else:
		finishInstall()

def mountEFIPart():
	partTypes  = runShellCommand("fdisk -lo device,type | awk '!/^($|I|D|U|S|A|T)/ {print $2}'").split('\n')
	partNames  = runShellCommand("fdisk -lo device,type | awk '!/^($|I|D|U|S|A|T)/ {print $1}'").split('\n')
	try:
		efipart = partNames[partTypes.index('EFI')]
		os.system("mount {} /mnt/boot/efi".format(efipart))
	except ValueError:
		d.infobox(title="Hata !",text="Sisteminizde EFI Sistem bölümünü bulunamadı. Bu bölümün olup olmadığını kontrol ediniz.\
		Eğer bölümün olduğuna eminseniz https://github.com/milisarge/malfs-milis/issues adresinden bug bildiriminde bulunabilirsiniz.")
		sys.exit()

def installGrub(target):
	os.system("mount --bind /dev /mnt/dev")
	os.system("mount --bind /sys /mnt/sys")
	os.system("mount --bind /proc /mnt/proc")
	
	if isEFI():
		try:
			os.mkdir("/mnt/boot/efi")
		except:
			pass
		
		mountEFIPart()
		os.system("chroot /mnt grub-install --efi-directory=/boot/efi --target=x86_64-efi --bootloader-id=Milis {}".format(target[:-1]))
		log.write('[+] Grub kuruldu: {}\n'.format(target[:-1]))
		os.system("chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")
	else:
		target = target[:-1]
		if target == "/dev/mmcblk0": #SD kart'a kurulum fix (deneysel)
			os.system("grub-install --boot-directory=/mnt/boot /dev/mmcblk0")
		else:
			os.system("grub-install --boot-directory=/mnt/boot " + target)
		os.system("chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")
		log.write('[+] Grub kuruldu: {}\n'.format(target))
	finishInstall()
	
def finishInstall():
	d.infobox(text="Milis GNU/Linux sisteminize kuruldu. Eğer herşeyin yolunda gittiğini düşünüyorsanız /tmp/kurulum.log dosyasının yedeğini alıp sistemi yeniden başlatabilirsin :)",width=70)
		
def chooseSwap(part):
	swapChoice = []
	validParts = ['sd','hd','mmcblk0p']
	#Şimdilik Parted kütüphanesine gerek kalmadı, lsblk istediğimiz bütün değerleri alıyor.
	diskParts  = runShellCommand("lsblk -ln -o  NAME    | awk '{print $1}'").split('\n')
	partSizes  = runShellCommand("lsblk -ln -o  SIZE    | awk '{print $1}'").split('\n')
	partFs     = runShellCommand("lsblk -ln -o  FSTYPE  | awk '{print $1}'").split('\n')
	partMajmin = runShellCommand("lsblk -ln -o  MAJ:MIN | awk '{print $1}'").split('\n')
	partLabel  = runShellCommand("lsblk -ln -o  LABEL").split('\n') #Bunda awk yok çünkü arada boşluk olabilir. 
	for i in range(len(diskParts)-1):
		if partMajmin[i].split(":")[1] != "0": # partition olmayanları ele (sda/sdb swap için uygun değil)
			if diskParts[i] != part:
				for validPart in validParts: 
					if validPart in diskParts[i]: #loop partlar gibi swap kurulamayacak alanları ele
						swapChoice.append((diskParts[i],partLabel[i]+ "\t" +partSizes[i]+"\t"+partFs[i]))
	log.write("Takas alanı için uygun disk bölümleri:\n")
	for disqPart in swapChoice:
		log.write("{} {}\n".format(disqPart[0],disqPart[1]))
	log.write('\n')

	status,selectedPart = d.menu(title="Adım 2: Disk İşlemleri",text="Takas alanının yer alacağı disk bölümünü seçiniz:",choices=swapChoice,width=70)
	if status == "ok":
		log.write("[+] Takas alanı seçildi:  {}\n".format(selectedPart))
		setSwap(selectedPart)
		
def setSwap(part):
	os.system("mkswap "+"/dev/"+part)
	os.system('echo "`lsblk -ln -o UUID /dev/' + part + '` none swap sw 0 0" | tee -a /etc/fstab')
		 
if __name__ == "__main__":

	greetingDialog()
