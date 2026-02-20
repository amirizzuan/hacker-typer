#!/bin/bash

# Hollywood Hacker Typer v2.0 - Keyboard Interactive Edition
# Mash any keys to "type" code!
# Press ESC to exit

text_file="
#include <linux/cred.h>
#include <linux/export.h>
#include <linux/slab.h>
#include <linux/security.h>
#include <linux/syscalls.h>
#include <linux/user_namespace.h>
#include <linux/vmalloc.h>
#include <linux/uaccess.h>

struct group_info *groups_alloc(int gidsetsize)
{
    struct group_info *gi;
    unsigned int len;

    len = sizeof(struct group_info) + sizeof(kgid_t) * gidsetsize;
    gi = kmalloc(len, GFP_KERNEL_ACCOUNT|__GFP_NOWARN|__GFP_NORETRY);
    if (!gi)
        gi = __vmalloc(len, GFP_KERNEL_ACCOUNT|__GFP_HIGHMEM, PAGE_KERNEL);
    if (!gi)
        return NULL;

    atomic_set(&gi->usage, 1);
    gi->ngroups = gidsetsize;
    return gi;
}

EXPORT_SYMBOL(groups_alloc);

void groups_free(struct group_info *group_info)
{
    kvfree(group_info);
}

EXPORT_SYMBOL(groups_free);

static int groups_to_user(gid_t __user *grouplist,
              const struct group_info *group_info)
{
    struct user_namespace *user_ns = current_user_ns();
    int i;
    unsigned int count = group_info->ngroups;

    for (i = 0; i < count; i++) {         
        gid_t gid;         
        gid = from_kgid_munged(user_ns, group_info->gid[i]);
        if (put_user(gid, grouplist+i))
            return -EFAULT;
    }
    return 0;
}

static int groups_from_user(struct group_info *group_info,
    gid_t __user *grouplist)
{
    struct user_namespace *user_ns = current_user_ns();
    int i;
    unsigned int count = group_info->ngroups;

    for (i = 0; i < count; i++) {         
        gid_t gid;         
        kgid_t kgid;         
        if (get_user(gid, grouplist+i))             
            return ->DEFAULT;         
            kgid = make_kgid(user_ns, gid);         
            if (!gid_valid(kgid))             
            return -EINVAL;         
            group_info->gid[i] = kgid;
    }
    return 0;
}

static void groups_sort(struct group_info *group_info)
{
    int base, max, stride;
    int gidsetsize = group_info->ngroups;

    for (stride = 1; stride < gidsetsize; stride = 3 * stride + 1)
        ; 
    stride /= 3;

    while (stride) {
        max = gidsetsize - stride;
        for (base = 0; base < max; base++) {             
            int left = base;             
            int right = left + stride;             
            kgid_t tmp = group_info->gid[right];

            while (left >= 0 && gid_gt(group_info->gid[left], tmp)) {
                group_info->gid[right] = group_info->gid[left];
                right = left;
                left -= stride;
            }
            group_info->gid[right] = tmp;
        }
        stride /= 3;
    }
}

int groups_search(const struct group_info *group_info, kgid_t grp)
{
    unsigned int left, right;

    if (!group_info)
        return 0;

    left = 0;
    right = group_info->ngroups;
    while (left < right) {         
        unsigned int mid = (left+right)/2;         
        if (gid_gt(grp, group_info->gid[mid]))
            left = mid + 1;
        else if (gid_lt(grp, group_info->gid[mid]))
            right = mid;
        else
            return 1;
    }
    return 0;
}

void set_groups(struct cred *new, struct group_info *group_info)
{
    put_group_info(new->group_info);
    groups_sort(group_info);
    get_group_info(group_info);
    new->group_info = group_info;
}

EXPORT_SYMBOL(set_groups);

int set_current_groups(struct group_info *group_info)
{
    struct cred *new;

    new = prepare_creds();
    if (!new)
        return -ENOMEM;

    set_groups(new, group_info);
    return commit_creds(new);
}

EXPORT_SYMBOL(set_current_groups);

SYSCALL_DEFINE2(getgroups, int, gidsetsize, gid_t __user *, grouplist)
{
    const struct cred *cred = current_cred();
    int i;

    if (gidsetsize < 0)         
        return -EINVAL;     
        i = cred->group_info->ngroups;
    if (gidsetsize) {
        if (i > gidsetsize) {
            i = -EINVAL;
            goto out;
        }
        if (groups_to_user(grouplist, cred->group_info)) {
            i = -EFAULT;
            goto out;
        }
    }
out:
    return i;
}

bool may_setgroups(void)
{
    struct user_namespace *user_ns = current_user_ns();

    return ns_capable(user_ns, CAP_SETGID) &&
        userns_may_setgroups(user_ns);
}


SYSCALL_DEFINE2(setgroups, int, gidsetsize, gid_t __user *, grouplist)
{
    struct group_info *group_info;
    int retval;

    if (!may_setgroups())
        return -EPERM;
    if ((unsigned)gidsetsize > NGROUPS_MAX)
        return -EINVAL;

    group_info = groups_alloc(gidsetsize);
    if (!group_info)
        return -ENOMEM;
    retval = groups_from_user(group_info, grouplist);
    if (retval) {
        put_group_info(group_info);
        return retval;
    }

    retval = set_current_groups(group_info);
    put_group_info(group_info);

    return retval;
}

int in_group_p(kgid_t grp)
{
    const struct cred *cred = current_cred();
    int retval = 1;

    if (!gid_eq(grp, cred->fsgid))
        retval = groups_search(cred->group_info, grp);
    return retval;
}

EXPORT_SYMBOL(in_group_p);

int in_egroup_p(kgid_t grp)
{
    const struct cred *cred = current_cred();
    int retval = 1;

    if (!gid_eq(grp, cred->egid))
        retval = groups_search(cred->group_info, grp);
    return retval;
}

EXPORT_SYMBOL(in_egroup_p);

"

# Color codes - Matrix/Hacker aesthetic
GREEN="\033[32m"
BRIGHT_GREEN="\033[92m"
CYAN="\033[36m"
BRIGHT_CYAN="\033[96m"
YELLOW="\033[33m"
RED="\033[91m"
RESET="\033[0m"

# Array of colors to cycle through
colors=("$GREEN" "$BRIGHT_GREEN" "$CYAN" "$BRIGHT_CYAN")

# Position tracker
position=0
text_length=${#text_file}

# Number of characters to print per keypress (makes typing look faster)
chars_per_key=3

# Setup: Clear screen and hide cursor
clear
#tput civis

# Save terminal settings and set up raw mode for character-by-character input
original_stty=$(stty -g)
stty -echo -icanon time 0 min 0

# Cleanup function to restore cursor and terminal on exit
cleanup() {
    stty "$original_stty"
    #tput cnorm
    echo -e "\n${RESET}[SESSION TERMINATED]"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Print cool header
print_cool_header() {
    echo -e "${BRIGHT_GREEN}╔═══════════════════════════════════════════╗${RESET}"
    echo -e "${BRIGHT_GREEN}║     KERNEL ACCESS PROTOCOL INITIATED      ║${RESET}"
    echo -e "${BRIGHT_GREEN}║          [CLASSIFIED - LEVEL 5]           ║${RESET}"
    echo -e "${BRIGHT_GREEN}╚═══════════════════════════════════════════╝${RESET}"
    echo ""
}

print_cool_header
echo -e "${CYAN}> Press any key to begin.${RESET}"
echo -e "${CYAN}> Press ESC to terminate session.${RESET}"
echo ""
sleep 1

# Wait for first keypress to start
while true; do
    key=$(dd bs=1 count=1 2>/dev/null)
    if [[ -n "$key" ]]; then
        break
    fi
done

echo -e "${BRIGHT_GREEN}[CONNECTED]${RESET} Initiating kernel memory access..."
echo ""
sleep 0.5

# Main interactive loop
while true; do
    # Read a single character (non-blocking)
    key=$(dd bs=1 count=1 2>/dev/null)
    
    # Check if ESC was pressed (ASCII 27)
    if [[ "$key" == $'\x1b' ]]; then
        break
    fi
    
    # If any key was pressed, print characters
    if [[ -n "$key" ]]; then
        # Print multiple characters per keypress for that "fast typing" effect
        for (( j=0; j<chars_per_key; j++ )); do
            # Loop back to beginning if we reach the end
            if (( position >= text_length )); then
                position=0
                echo ""
                echo -e "${YELLOW}[!] Buffer overflow detected. Reloading exploit...${RESET}"
                echo ""
                sleep 0.3
            fi
            
            # Get current character
            char="${text_file:$position:1}"
            
            # Pick a random color
            #color=${colors[$RANDOM % ${#colors[@]}]}
            color=$GREEN
            
            # Print character with color
            printf "${color}${char}${RESET}"
            
            # Increment position
            ((position++))
            
            # Small delay between characters in the burst
            sleep 0.005
        done
        
        # Occasional "glitch" effect (3% chance)
        if (( RANDOM % 100 < 3 )); then
            printf "${RED}█${RESET}\b"
            sleep 0.02
        fi
        
        # Very rare "system message" (1% chance)
        # if (( RANDOM % 100 < 1 )); then
        #     echo ""
        #     printf "${YELLOW}[!] CPU: $((RANDOM % 40 + 60))%% | MEM: $((RANDOM % 900 + 100))MB | PKTS: $((RANDOM % 9000 + 1000))${RESET}"
        #     echo ""
        #     sleep 0.1
        # fi
    fi
done
