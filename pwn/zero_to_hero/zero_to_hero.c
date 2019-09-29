
// 0x602060
void * power[7];

// 0x400997
void show_menu()
{
  puts("1. Get a superpower");
  puts("2. Remove a superpower");
  puts("3. Exit");
}

// 0x4009C2
int find_free_slot()
{
  signed int i; // [rsp+0h] [rbp-4h]

  for (i = 0; i < 7; ++i)
  {
    if (!power[i])
      return i;
  }

  return -1;
}

// 0x400A02
void win()
{
  FILE * fp; // [rsp+8h] [rbp-8h]

  fp = fopen("flag.txt", "r");
  if (fp) {
    while ((int ch = fgetc(fp)) != EOF) {
      putchar(ch);
    }
  }
}

// 0x400a4d
void get_super_power()
{
  _BYTE *v0; // rbx
  unsigned int size;
  int index; // [rsp+0h] [rbp-20h]
  unsigned __int64 canary; // [rsp+8h] [rbp-18h]

  int index = find_free_slot();
  if (index < 0)
  {
    puts("You have too many powers!");
    exit(-1);
  }

  puts("Describe your new power.");
  puts("What is the length of your description?");
  printf("> ");
  scanf("%u", &size);
  getchar();

  if (size > 0x408)
  {
    puts("Power too strong!");
    exit(-1);
  }

  power[size] = malloc(size);
  puts("Enter your description: ");
  printf("> ");

  v0 = power[size];

  // this trailing zero will overrun into chunk header
  // when size is multiple of sizeof(size_t) == 0x8,
  // it will change the size of the next chunk
  v0[read(0, power[size], size)] = 0;

  puts("Done!");
}

// 0x400bb3
void remove_super_power()
{
  unsigned int index; // [rsp+4h] [rbp-Ch]
  unsigned __int64 canary; // [rsp+8h] [rbp-8h]

  index = 0;
  puts("Which power would you like to remove?");
  printf("> ");
  scanf("%u", &index);
  getchar();
  if ( index > 6 )
  {
    puts("Invalid index!");
    exit(-1);
  }
  
  free(power[index]);
}

void main(int argc, char **argc, char **envp)
{
  int choice; // [rsp+Ch] [rbp-24h]
  char buf[24]; // [rsp+10h] [rbp-20h]
  unsigned __int64 canary; // [rsp+28h] [rbp-8h]

  setvbuf(stdin, 0LL, 2, 0LL);
  setvbuf(stdout, 0LL, 2, 0LL);
  setvbuf(stderr, 0LL, 2, 0LL);

  puts("From Zero to Hero");
  puts("So, you want to be a hero?");
  buf[read(0, buf, 20)] = 0;
  if (buf[0] != 'y') {
    puts("No? Then why are you even here?");
    exit(0);
  }
  puts("Really? Being a hero is hard.");
  puts("Fine. I see I can't convince you otherwise.");
  printf("It's dangerous to go alone. Take this: %p\n", &system);

  while (1) {
    show_menu();
    printf("> ");
    choice = 0;
    scanf("%d", &choice);
    getchar();
    switch(choice) {
    case 1:
      get_super_power();
      break;

    case 2:
      remove_super_power();
      break;

    case 3:
      puts("Giving up?");
      // fall thru

    default:
      exit(0);
    }
  }
}
