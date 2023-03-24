
echo "Fetching from git to client1"
sudo rm -r ntua-distributed-systems
git clone https://github.com/nickbel7/ntua-distributed-systems.git
echo "Succesfully fetched data"

echo "Copying to Client 2"
scp -rp /home/user/ntua-distributed-systems client2:/home/user/
echo "Copying to Client 3"
scp -rp /home/user/ntua-distributed-systems client3:/home/user/
echo "Copying to Client 4"
scp -rp /home/user/ntua-distributed-systems client4:/home/user/
echo "Copying to Client 5"
scp -rp /home/user/ntua-distributed-systems client5:/home/user/