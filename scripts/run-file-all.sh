echo "Enter command"
read command

echo "Client 1"
ssh client1 "$command"
echo "Client 2"
ssh client2 "$command"
echo "Client 3"
ssh client3 "$command"
echo "Client 4"
ssh client4 "$command"
echo "Client 5"
ssh client5 "$command"