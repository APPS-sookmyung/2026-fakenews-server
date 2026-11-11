package com.fakenews.server;

import com.fakenews.server.domain.auth.User;
import com.fakenews.server.domain.auth.UserRepository;
import com.fakenews.server.domain.participant.ParticipantRepository;
import com.fakenews.server.domain.participant.entity.Participant;
import com.fakenews.server.domain.post.repository.PostRepository;
import com.fakenews.server.domain.simulation.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class ParticipantProfileTests {
    @Autowired MockMvc mvc;
    @Autowired ParticipantRepository participants;
    @Autowired SimulationRepository simulations;
    @Autowired UserRepository users;
    @Autowired PostRepository posts;
    private User owner, member, outsider;
    private Simulation simulation, other;
    private Participant ai, human;

    @BeforeEach
    void setup() {
        owner = users.save(new User("owner@example.com", "unused", "소유자"));
        member = users.save(new User("member@example.com", "unused", "참여자"));
        outsider = users.save(new User("outside@example.com", "unused", "외부인"));
        simulation = simulations.save(Simulation.create(owner.getId(), "실험"));
        other = simulations.save(Simulation.create(outsider.getId(), "다른 실험"));
        ai = participants.saveAndFlush(Participant.create(simulation.getId(), null, "독서가", "주말에 도서관 이용", List.of("독서")));
        human = participants.saveAndFlush(Participant.create(simulation.getId(), member.getId(), "사람", "성향", List.of()));
    }

    private String root() { return "/api/simulations/" + simulation.getId() + "/participants"; }
    private String profile() { return root() + "/" + ai.getId() + "/profile"; }
    private String postPath(Participant participant) { return root() + "/" + participant.getId() + "/posts"; }
    private String persona() { return "{\"displayName\":\"새 이름\",\"description\":\"새 성향\",\"interests\":[\"과학\"]}"; }

    @Test
    void onlyOwnerAndMembersCanReadProfiles() throws Exception {
        for (User reader : List.of(owner, member)) {
            mvc.perform(get(profile()).with(user(reader.getEmail())))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.participantId").value(ai.getId()))
                    .andExpect(jsonPath("$.simulationId").value(simulation.getId()))
                    .andExpect(jsonPath("$.description").value("주말에 도서관 이용"))
                    .andExpect(jsonPath("$.interests[0]").value("독서"))
                    .andExpect(jsonPath("$.userId").doesNotExist());
        }
        mvc.perform(get(profile())).andExpect(status().isUnauthorized());
        mvc.perform(get(profile()).with(user(outsider.getEmail()))).andExpect(status().isForbidden());
        mvc.perform(get(profile()).with(user("missing@example.com"))).andExpect(status().isUnauthorized());
        mvc.perform(get("/api/simulations/" + other.getId() + "/participants/" + ai.getId() + "/profile")
                .with(user(outsider.getEmail()))).andExpect(status().isNotFound());
    }

    @Test
    void createsSimulationWithAuthenticatedOwnerAndControlsRead() throws Exception {
        long count = simulations.count();
        mvc.perform(post("/api/simulations").with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"새 실험\",\"ownerUserId\":" + outsider.getId() + "}"))
                .andExpect(status().isCreated()).andExpect(jsonPath("$.simulationId").isNumber());
        assertThat(simulations.count()).isEqualTo(count + 1);
        assertThat(simulations.findAll().stream().filter(s -> s.getName().equals("새 실험")).findFirst().orElseThrow().getOwnerUserId())
                .isEqualTo(owner.getId());
        mvc.perform(get("/api/simulations/" + simulation.getId()).with(user(member.getEmail()))).andExpect(status().isOk());
        mvc.perform(get("/api/simulations/" + simulation.getId()).with(user(outsider.getEmail()))).andExpect(status().isForbidden());
        mvc.perform(post("/api/simulations").with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\" \"}")).andExpect(status().isBadRequest());
    }

    @Test
    void ownerCreatesAndUpdatesParticipantsButOthersCannot() throws Exception {
        mvc.perform(post(root()).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(persona()))
                .andExpect(status().isCreated()).andExpect(jsonPath("$.description").value("새 성향"));
        for (User denied : List.of(member, outsider)) {
            mvc.perform(post(root()).with(user(denied.getEmail())).contentType(MediaType.APPLICATION_JSON).content(persona()))
                    .andExpect(status().isForbidden());
            mvc.perform(put(profile()).with(user(denied.getEmail())).contentType(MediaType.APPLICATION_JSON).content(persona()))
                    .andExpect(status().isForbidden());
        }
        mvc.perform(put(profile()).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(persona()))
                .andExpect(status().isOk()).andExpect(jsonPath("$.interests[0]").value("과학"));
        assertThat(participants.findById(ai.getId()).orElseThrow().getDescription()).isEqualTo("새 성향");
    }

    @Test
    void validatesMembershipCreationAndPersonaWithoutPartialWrites() throws Exception {
        long count = participants.count();
        String duplicate = persona().replace("{", "{\"userId\":" + member.getId() + ",");
        mvc.perform(post(root()).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(duplicate))
                .andExpect(status().isConflict());
        mvc.perform(post(root()).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON)
                .content(persona().replace("{", "{\"userId\":999999,"))).andExpect(status().isNotFound());
        for (String invalid : List.of("{}", persona().replace("새 성향", " "), persona().replace("[\"과학\"]", "null"),
                persona().replace("과학", " "))) {
            mvc.perform(post(root()).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(invalid))
                    .andExpect(status().isBadRequest());
            mvc.perform(put(profile()).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(invalid))
                    .andExpect(status().isBadRequest());
        }
        assertThat(participants.count()).isEqualTo(count);
        assertThat(participants.findById(ai.getId()).orElseThrow().getDescription()).isEqualTo("주말에 도서관 이용");
        String newMember = persona().replace("{", "{\"userId\":" + outsider.getId() + ",");
        mvc.perform(post(root()).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(newMember))
                .andExpect(status().isCreated());
        mvc.perform(get(profile()).with(user(outsider.getEmail()))).andExpect(status().isOk());
    }

    @Test
    void linksPostsAndBlocksImpersonationAndReadBypass() throws Exception {
        String body = "{\"content\":\"실험 게시글\",\"userId\":999,\"participantId\":999,\"simulationId\":999}";
        mvc.perform(post(postPath(human)).with(user(member.getEmail())).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isCreated());
        var saved = posts.findAll().get(0);
        assertThat(saved.getSimulationId()).isEqualTo(simulation.getId());
        assertThat(saved.getParticipantId()).isEqualTo(human.getId());
        assertThat(saved.getUserId()).isEqualTo(member.getId());
        for (String route : List.of("/api/posts/", "/post/")) {
            mvc.perform(get(route + saved.getPostId()).with(user(outsider.getEmail()))).andExpect(status().isForbidden());
            mvc.perform(get(route + saved.getPostId()).with(user(owner.getEmail()))).andExpect(status().isOk());
        }
        mvc.perform(post(postPath(ai)).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isCreated());
        var aiPost = posts.findAll().stream().filter(p -> p.getParticipantId().equals(ai.getId())).findFirst().orElseThrow();
        assertThat(aiPost.getUserId()).isNull();
        assertThat(aiPost.getSimulationId()).isEqualTo(simulation.getId());
        mvc.perform(post(postPath(human)).with(user(owner.getEmail())).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isForbidden());
        mvc.perform(post(postPath(ai)).with(user(member.getEmail())).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isForbidden());
        mvc.perform(post(postPath(human)).with(user(outsider.getEmail())).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isForbidden());
        mvc.perform(post("/api/simulations/" + other.getId() + "/participants/" + ai.getId() + "/posts")
                .with(user(outsider.getEmail())).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isNotFound());
        assertThat(posts.count()).isEqualTo(2);
    }
}
